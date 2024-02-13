import argparse
import os
from typing import List
from pyulog.core import ULog
import logging
import sys
import pathlib
import time

from roboto.association import (
    Association,
    AssociationType,
)
from roboto.domain import actions, datasets, files, topics
from roboto.http import (
    HttpClient,
    SigV4AuthDecorator,
)
from roboto.transactions import TransactionManager

import ulog_to_mcap.utils as utils

log = logging.getLogger("Ingesting ULog files to Roboto")


def load_env_var(env_var: actions.InvocationEnvVar) -> str:
    """
    Load an environment variable, and exit if it is not found.

    Args:
        env_var: The environment variable to load.

    Returns:
        The value of the environment variable.
    """
    value = os.getenv(env_var.value)
    if not value:
        log.error("Missing required ENV var: '%s'", env_var)
        sys.exit(1)
    return value


def setup_env():
    """
    Set up the environment for the action.

    Returns:
        A tuple containing the organization ID, input directory, topic delegate, and dataset.
    """
    roboto_service_url = load_env_var(actions.InvocationEnvVar.RobotoServiceUrl)
    org_id = load_env_var(actions.InvocationEnvVar.OrgId)
    invocation_id = load_env_var(actions.InvocationEnvVar.InvocationId)
    input_dir = load_env_var(actions.InvocationEnvVar.InputDir)
    output_dir = load_env_var(actions.InvocationEnvVar.OutputDir)

    http_client = HttpClient(default_auth=SigV4AuthDecorator("execute-api"))

    topic_delegate = topics.TopicHttpDelegate(
        roboto_service_base_url=roboto_service_url, http_client=http_client
    )

    invocation = actions.Invocation.from_id(
        invocation_id,
        invocation_delegate=actions.InvocationHttpDelegate(
            roboto_service_base_url=roboto_service_url, http_client=http_client
        ),
        org_id=org_id,
    )
    dataset = datasets.Dataset.from_id(
        invocation.data_source.data_source_id,
        datasets.DatasetHttpDelegate(
            roboto_service_base_url=roboto_service_url, http_client=http_client
        ),
        files.FileClientDelegate(
            roboto_service_base_url=roboto_service_url, http_client=http_client
        ),
        transaction_manager=TransactionManager(
            roboto_service_base_url=roboto_service_url, http_client=http_client
        ),
    )

    return org_id, input_dir, output_dir, topic_delegate, dataset


def ingest_ulog(ulog_file_path: str, messages: List[str] = None):
    """
    For each message in the .ulg file, a .mcap file is created.
    The .mcap files are then uploaded to Roboto. For each message, a topic is created in Roboto,
    message paths are added to the topic and a default representation is set for the topic.

    Args:
        ulog_file_path: Path to the .ulg file.
        messages: List of messages to process, separated by commas.

    Returns:
        None
    """
    msg_filter = messages.split(",") if messages else None
    print(ulog_file_path)

    ulog = ULog(ulog_file_path, msg_filter, True)

    # Setup Environment
    org_id, input_dir, output_dir, topic_delegate, dataset = setup_env()
    output_dir_path_mcap, output_dir_temp = utils.setup_output_folder_structure(ulog_file_path, input_dir)

    schema_registry_dict = {}
    schema_checksum_dict = {}

    for key in ulog.message_formats:
        json_schema_topic = utils.create_json_schema(ulog.message_formats[key].fields)
        schema_registry_dict[key] = json_schema_topic
        schema_checksum_dict[key] = utils.compute_checksum(json_schema_topic)

    dataset_relative_path = pathlib.Path(ulog_file_path).relative_to(input_dir)
    file_record = dataset.get_file_info(dataset_relative_path)

    topic_association = Association(
        association_id=file_record.file_id,
        association_type=AssociationType.File
    )

    start_time = time.time()

    # This is a temporary fix for Multi Information messages with the same name
    # https://docs.px4.io/main/en/dev_log/ulog_file_format.html#m-multi-information-message
    # TODO: handle this in a better way
    message_names_with_multi_id_list = list()
    for d in sorted(ulog.data_list, key=lambda obj: obj.name):
        if d.multi_id > 0:
            message_names_with_multi_id_list.append(d.name)

    message_names_with_multi_id_list = list(set(message_names_with_multi_id_list))

    print(f"message_names_with_multi_id_list: {message_names_with_multi_id_list}")

    for d in sorted(ulog.data_list, key=lambda obj: obj.name):
        topic_name = schema_name = d.name

        if topic_name in schema_registry_dict.keys():
            if topic_name in message_names_with_multi_id_list:
                topic_name = topic_name + "_" + str(d.multi_id).zfill(2)

            message_count = len(d.data["timestamp"])
            schema_checksum = schema_checksum_dict[schema_name]

            # Create Topic Record
            topic = topics.Topic.create(
                request=topics.CreateTopicRequest(
                    association=topic_association,
                    org_id=org_id,
                    schema_name=schema_name,
                    schema_checksum=schema_checksum,
                    topic_name=topic_name,
                    message_count=message_count,
                    # start_time=start_time,
                    # end_time=end_time,
                ),
                topic_delegate=topic_delegate,
            )
            print(f"Topic created: {topic_name}")

            # Create Message Path Records
            utils.create_message_path_records(topic, d.field_data)

            # Create MCAP File
            output_path_per_topic_mcap = os.path.join(output_dir_path_mcap, f"{topic_name}.mcap")
            print(f"MCAP file path: {output_path_per_topic_mcap}")

            utils.create_per_topic_mcap_from_ulog(output_path_per_topic_mcap,
                                                  d,
                                                  schema_registry_dict)

            relative_file_name = output_path_per_topic_mcap.split(output_dir_temp)[1]
            relative_file_name = relative_file_name[1:]

            # Upload MCAP File
            dataset.upload_file(pathlib.Path(output_path_per_topic_mcap), relative_file_name)

            print(f"Setting default representation for topic: {topic_name}, "
                  f"file_id: {dataset.get_file_info(relative_file_name).file_id}")

            # Set Default Topic Representation
            topic.set_default_representation(
                request=topics.SetDefaultRepresentationRequest(
                    association=Association(
                        association_type=AssociationType.File,
                        association_id=dataset.get_file_info(relative_file_name).file_id,
                    ),
                    org_id=org_id,
                    storage_format=topics.RepresentationStorageFormat.MCAP,
                    version=1,
                )
            )

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"The topic create function took {elapsed_time} seconds to run.")


parser = argparse.ArgumentParser()
parser.add_argument(
    "-i",
    "--input-dir",
    dest="input_dir",
    type=pathlib.Path,
    required=False,
    help="Directory containing input files to process",
    default=os.environ.get(actions.InvocationEnvVar.InputDir.value),
)

parser.add_argument(
    "-o",
    "--output-dir",
    dest="output_dir",
    type=pathlib.Path,
    required=False,
    help="Directory to which to write any output files to be uploaded",
    default=os.environ.get(actions.InvocationEnvVar.OutputDir.value),
)

parser.add_argument(
    "-m",
    "--messages",
    dest="messages",
    type=str,
    required=False,
    help="List of messages to process, separated by commas",
    default=os.environ.get("ROBOTO_PARAM_MESSAGES", None),
)

args = parser.parse_args()

for root, dirs, f in os.walk(args.input_dir):
    for file in f:
        if file.endswith(".ulg"):
            full_path = os.path.join(root, file)
            ingest_ulog(
                ulog_file_path=full_path,
                messages=args.messages,
            )
