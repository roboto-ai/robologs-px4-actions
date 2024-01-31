import argparse
import os
import tempfile
from typing import List
from pyulog.core import ULog
import logging
import sys
import pathlib

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

log = logging.getLogger("Converting .ulg to .mcap")


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

    return org_id, input_dir, topic_delegate, dataset


def ulog_to_mcap(ulog_file_path: str, messages: List[str] = None):
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
    disable_str_exceptions = True
    print(ulog_file_path)

    temp_dir = tempfile.TemporaryDirectory()
    ulog = ULog(ulog_file_path, msg_filter, disable_str_exceptions)

    # Setup environment
    org_id, input_dir, topic_delegate, dataset = setup_env()

    # Create Topic Records
    schema_registry_dict = {}
    schema_checksum_dict = {}

    for key in ulog.message_formats:
        json_schema_topic = utils.create_json_schema(ulog.message_formats[key].fields)
        schema_registry_dict[key] = json_schema_topic
        schema_checksum_dict[key] = utils.compute_checksum(json_schema_topic)

    topic_name_to_file_id_dict = utils.create_per_topic_mcap_from_ulog(
        ulog=ulog, output_folder_path=str(temp_dir.name), dataset=dataset
    )

    dataset_relative_path = pathlib.Path(ulog_file_path).relative_to(input_dir)
    file_record = dataset.get_file_info(dataset_relative_path)

    topic_association = Association(
        association_id=file_record.file_id, association_type=AssociationType.File
    )

    topic_list = list()

    for d in sorted(ulog.data_list, key=lambda obj: obj.name):
        topic_name = schema_name = d.name

        # This is a temporary fix for Multi Information messages with the same name
        # https://docs.px4.io/main/en/dev_log/ulog_file_format.html#m-multi-information-message
        # TODO: handle this in a better way
        if topic_name in schema_registry_dict.keys():
            if topic_name in topic_list:
                continue
            topic_list.append(topic_name)

            message_count = len(d.data["timestamp"])
            schema_checksum = schema_checksum_dict[schema_name]

            # Creating topic
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
        array_list = list()

        for field in d.field_data:
            # for now only allow these types
            if field.type_str in utils.TYPE_MAPPING_CANONICAL.keys():
                if "[" in field.field_name:
                    array_name = field.field_name.split("[")[0]
                    if array_name not in array_list:
                        print(
                            f"Adding array: {array_name}, type: {field.type_str}, canonical: {topics.CanonicalDataType.Array}"
                        )
                        topic.add_message_path(
                            request=topics.AddMessagePathRequest(
                                message_path=array_name,
                                data_type=field.type_str,
                                canonical_data_type=topics.CanonicalDataType.Array,
                            )
                        )
                        array_list.append(array_name)
                else:
                    print(
                        f"Adding field: {field.field_name}, type: {field.type_str}, canonical: {utils.TYPE_MAPPING_CANONICAL[field.type_str]}"
                    )
                    topic.add_message_path(
                        request=topics.AddMessagePathRequest(
                            message_path=field.field_name,
                            data_type=field.type_str,
                            canonical_data_type=utils.TYPE_MAPPING_CANONICAL[
                                field.type_str
                            ],
                        )
                    )
        if topic_name in topic_name_to_file_id_dict.keys():
            print(
                f"Setting default representation for topic: {topic_name}, file_id: {topic_name_to_file_id_dict[topic_name]}"
            )
            topic.set_default_representation(
                request=topics.SetDefaultRepresentationRequest(
                    association=Association(
                        association_type=AssociationType.File,
                        association_id=topic_name_to_file_id_dict[topic_name],
                    ),
                    org_id=org_id,
                    storage_format=topics.RepresentationStorageFormat.MCAP,
                    version=1,
                )
            )


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
            # _, ulg_file_name = os.path.split(file)
            # ulg_output_folder_name = ulg_file_name.replace(".ulg", "")
            # output_folder = os.path.join(args.output_dir, ulg_output_folder_name)
            #
            # if not os.path.exists(output_folder):
            #     os.makedirs(output_folder, exist_ok=True)

            full_path = os.path.join(root, file)
            ulog_to_mcap(
                ulog_file_path=full_path,
                messages=args.messages,
            )
