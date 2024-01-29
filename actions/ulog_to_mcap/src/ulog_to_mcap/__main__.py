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

from ulog_to_mcap.utils import create_per_topic_mcap_from_ulog, upload_mcap_files_to_dataset, TYPE_MAPPING_CANONICAL

log = logging.getLogger("Converting .ulg to .mcap")


def load_env_var(env_var: actions.InvocationEnvVar) -> str:
    value = os.getenv(env_var.value)
    if not value:
        log.error("Missing required ENV var: '%s'", env_var)
        sys.exit(1)
    return value


def ulog_to_mcap(
    ulog_file_path: str, output_folder_path: str, messages: List[str] = None
):
    """
    Convert a ULog file to a MCAP file.
    """
    msg_filter = messages.split(",") if messages else None
    disable_str_exceptions = True
    print(ulog_file_path)

    ROBOTO_SERVICE_URL = load_env_var(actions.InvocationEnvVar.RobotoServiceUrl)
    ORG_ID = load_env_var(actions.InvocationEnvVar.OrgId)
    INVOCATION_ID = load_env_var(actions.InvocationEnvVar.InvocationId)
    INPUT_DIR = load_env_var(actions.InvocationEnvVar.InputDir)

    http_client = HttpClient(default_auth=SigV4AuthDecorator("execute-api"))

    topic_delegate = topics.TopicHttpDelegate(
        roboto_service_base_url=ROBOTO_SERVICE_URL, http_client=http_client)

    invocation = actions.Invocation.from_id(
        INVOCATION_ID,
        invocation_delegate=actions.InvocationHttpDelegate(
            roboto_service_base_url=ROBOTO_SERVICE_URL, http_client=http_client
        ),
        org_id=ORG_ID,
    )
    dataset = datasets.Dataset.from_id(
        invocation.data_source.data_source_id,
        datasets.DatasetHttpDelegate(
            roboto_service_base_url=ROBOTO_SERVICE_URL, http_client=http_client
        ),
        files.FileClientDelegate(
            roboto_service_base_url=ROBOTO_SERVICE_URL, http_client=http_client
        ),
        transaction_manager=TransactionManager(
            roboto_service_base_url=ROBOTO_SERVICE_URL, http_client=http_client
        )
    )

    temp_dir = tempfile.TemporaryDirectory()

    ulog = ULog(ulog_file_path, msg_filter, disable_str_exceptions)

    schema_registry_dict, schema_checksum_dict = create_per_topic_mcap_from_ulog(
        ulog=ulog, output_folder_path=str(temp_dir.name)
    )

    upload_mcap_files_to_dataset(str(temp_dir.name), dataset)

    #
    # data = ulog.data_list
    #
    # dataset_relative_path = pathlib.Path(ulog_file_path).relative_to(INPUT_DIR)
    #
    # file_record = dataset.get_file_info(dataset_relative_path)
    #
    # topic_association = Association(
    #     association_id=file_record.file_id,
    #     association_type=AssociationType.File
    # )

    #
    # for d in data:
    #     topic_name = schema_name = d.name
    #     message_count = len(d.data["timestamp"])
    #     schema_checksum = schema_checksum_dict[schema_name]
    #
    #     # Creating topic
    #     topic = topics.Topic.create(
    #         request=topics.CreateTopicRequest(
    #             association=topic_association,
    #             org_id=ORG_ID,
    #             schema_name=schema_name,
    #             schema_checksum=schema_checksum,
    #             topic_name=topic_name,
    #             message_count=message_count,
    #             # start_time=start_time,
    #             # end_time=end_time,
    #         ),
    #         topic_delegate=topic_delegate,
    #     )
    #
    #     array_list = list()
    #
    #     for field in d.field_data:
    #         print(field.field_name)
    #         print(field.type_str)
    #
    #         # for now only allow these types
    #         if field.type_str in TYPE_MAPPING_CANONICAL.keys():
    #             if "[" in field.field_name:
    #                 array_name = field.field_name.split("[")[0]
    #                 if array_name not in array_list:
    #                     topic.add_message_path(
    #                         request=topics.AddMessagePathRequest(
    #                             message_path=field.field_name,
    #                             data_type=field.type_str,
    #                             canonical_data_type=topics.CanonicalDataType.Array
    #                         )
    #                     )
    #                     array_list.append(array_name)
    #                 else:
    #                     topic.add_message_path(
    #                         request=topics.AddMessagePathRequest(
    #                             message_path=field.field_name,
    #                             data_type=field.type_str,
    #                             canonical_data_type=TYPE_MAPPING_CANONICAL[field.type_str]
    #                         )
    #                     )

        # primary_representation = topic.set_default_representation(
        #     request=topics.SetDefaultRepresentationRequest(
        #         association=Association(
        #             association_type=AssociationType.File,
        #             association_id=dataset.add_file("per_topic.mcap").file_id,
        #         ),
        #         org_id=ORG_ID,
        #         storage_format=topics.RepresentationStorageFormat.MCAP,
        #         version=1,
        #     )
        # )


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
            _, ulg_file_name = os.path.split(file)
            ulg_output_folder_name = ulg_file_name.replace(".ulg", "")
            output_folder_path = os.path.join(args.output_dir, ulg_output_folder_name)

            if not os.path.exists(output_folder_path):
                os.makedirs(output_folder_path, exist_ok=True)

            full_path = os.path.join(root, file)
            ulog_to_mcap(
                ulog_file_path=full_path,
                output_folder_path=output_folder_path,
                messages=args.messages,
            )