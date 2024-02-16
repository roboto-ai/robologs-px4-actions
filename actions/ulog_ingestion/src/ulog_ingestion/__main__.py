import argparse
import os
from typing import List
from pyulog.core import ULog
import logging
import sys
import pathlib
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

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

import ulog_ingestion.utils as utils

log = logging.getLogger("Ingesting ULog files to Roboto")


def load_env_var(env_var: actions.InvocationEnvVar) -> str:
    """
    Load an environment variable, and exit if it is not found.

    Args:
    - env_var: The environment variable to load.

    Returns:
    - The value of the environment variable.
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
    - A tuple containing the organization ID, input directory, output directory, topic delegate, and dataset.
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


def process_data(
    ulog_file_path,
    ulog_data_object,
    ulog_message_format_object,
    message_names_with_multi_id_list,
    output_dir_path_mcap,
    output_dir_temp,
):
    """
    Process the data from a ULog file.

    Args:
    - ulog_file_path: Path to the .ulg file.
    - ulog_data_object: The ULog data object to process.
    - ulog_message_format_object: The ULog message object to process.
    - message_names_with_multi_id_list: A list of message names with multi IDs.
    - output_dir_path_mcap: The path to the output directory for the MCAP files.
    - output_dir_temp: The path to the temporary output directory.

    Returns:
    - None
    """
    org_id, input_dir, output_dir, topic_delegate, dataset = setup_env()

    dataset_relative_path = pathlib.Path(ulog_file_path).relative_to(input_dir)
    file_record = dataset.get_file_info(dataset_relative_path)

    topic_association = Association(
        association_id=file_record.file_id,
        association_type=AssociationType.File
    )

    topic_name = schema_name = topic_name_roboto = ulog_data_object.name

    if topic_name in message_names_with_multi_id_list:
        topic_name_roboto += "_" + str(ulog_data_object.multi_id).zfill(2)

    # See link below for more context about how pyulog organizes data
    # https://github.com/PX4/pyulog/blob/7819181f2c9cb0ecfbcd73d46571b0afa44f0d97/pyulog/core.py#L499-L503
    message_count = len(ulog_data_object.data["timestamp"])

    json_schema_topic = utils.create_json_schema(ulog_message_format_object[topic_name].fields)
    schema_checksum = utils.compute_checksum(json_schema_topic)

    # Create Topic Record
    start_time_ns = min(ulog_data_object.data["timestamp"]) * 1000
    end_time_ns = max(ulog_data_object.data["timestamp"]) * 1000

    topic = topics.Topic.create(
        request=topics.CreateTopicRequest(
            association=topic_association,
            org_id=org_id,
            schema_name=schema_name,
            schema_checksum=schema_checksum,
            topic_name=topic_name_roboto,
            message_count=message_count,
            start_time=start_time_ns,
            end_time=end_time_ns,
        ),
        topic_delegate=topic_delegate,
    )
    print(f"Topic created: {topic_name_roboto}")

    # Create Message Path Records
    utils.create_message_path_records(topic, ulog_data_object.field_data)

    # Create MCAP File
    output_path_per_topic_mcap = os.path.join(
        output_dir_path_mcap, f"{topic_name_roboto}.mcap"
    )
    print(f"MCAP file path: {output_path_per_topic_mcap}")
    utils.create_per_topic_mcap_from_ulog(
        output_path_per_topic_mcap, ulog_data_object, json_schema_topic
    )

    relative_file_name = output_path_per_topic_mcap.split(output_dir_temp)[1][1:]

    # Upload MCAP File
    dataset.upload_file(
        pathlib.Path(output_path_per_topic_mcap), relative_file_name
    )

    file_id = dataset.get_file_info(relative_file_name).file_id

    print(
        f"Setting default representation for topic: {topic_name_roboto}, file_id: {file_id}"
    )

    # Set Default Topic Representation
    topic.set_default_representation(
        request=topics.SetDefaultRepresentationRequest(
            association=Association(
                association_type=AssociationType.File,
                association_id=file_id,
            ),
            org_id=org_id,
            storage_format=topics.RepresentationStorageFormat.MCAP,
            version=1,
        )
    )
    return


def ingest_ulog(ulog_file_path: str, topics: List[str] = None):
    """

    This function creates topic entries, message path records, and MCAP files from a ULog file.

    Args:
    - ulog_file_path: Path to the .ulg file.
    - messages: List of messages to process, separated by commas.

    Returns:
    - None
    """
    msg_filter = topics.split(",") if topics else None
    print(ulog_file_path)

    ulog = ULog(ulog_file_path, msg_filter, True)

    _, input_dir, _, _, _ = setup_env()

    output_dir_path_mcap, output_dir_temp = utils.setup_output_folder_structure(
        ulog_file_path, input_dir
    )
    start_time = time.time()

    # This is a temporary fix for Multi Information messages with the same name
    # https://docs.px4.io/main/en/dev_log/ulog_file_format.html#m-multi-information-message
    # Similar to Plotjuggler approach
    # TODO: handle this in a better way
    message_names_with_multi_id_list = list()
    for d in sorted(ulog.data_list, key=lambda obj: obj.name):
        print(f"topic name: {d.name}")
        if d.multi_id > 0:
            message_names_with_multi_id_list.append(d.name)

    message_names_with_multi_id_list = list(set(message_names_with_multi_id_list))

    print(f"message_names_with_multi_id_list: {message_names_with_multi_id_list}")

    # Prepare Arguments for Parallel Processing
    args_list = [
        (
            ulog_file_path,
            ulog_data_object,
            ulog.message_formats,
            message_names_with_multi_id_list,
            output_dir_path_mcap,
            output_dir_temp,
        )
        for ulog_data_object in sorted(ulog.data_list, key=lambda obj: obj.name)
    ]

    with ProcessPoolExecutor() as executor:
        # Submit all tasks and collect Future objects
        futures = [executor.submit(process_data, *args) for args in args_list]

        for future in as_completed(futures):
            try:
                print("Task completed successfully")
            except Exception as exc:
                print(f"Task generated an exception: {exc}")

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"The topic create function took {elapsed_time} seconds to process {ulog_file_path}.")


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
    "-t",
    "--topic-names",
    dest="topic_names",
    type=str,
    required=False,
    help="List of topic names to process, separated by commas",
    default=os.environ.get("ROBOTO_PARAM_TOPICS", None),
)

args = parser.parse_args()

for root, dirs, f in os.walk(args.input_dir):
    for file in f:
        full_path = os.path.join(root, file)
        if utils.is_valid_ulog(full_path):

            ingest_ulog(
                ulog_file_path=full_path,
                topics=args.topic_names,
            )
