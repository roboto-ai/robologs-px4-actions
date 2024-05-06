from pyulog.core import ULog
import argparse
import logging
import os
import pathlib
import json
from typing import Union
import re
import sys

from roboto.domain import actions, datasets, files, http_delegates
from roboto.env import RobotoEnvKey
from roboto.http import (
    HttpClient,
    SigV4AuthDecorator,
)
from roboto import updates

from roboto.transactions.transaction_manager import TransactionManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_env_var(env_var: RobotoEnvKey, strict=True) -> Union[str, None]:
    """
    Load an environment variable, and exit if it is not found.

    Args:
    - env_var: The environment variable to load.

    Returns:
    - The value of the environment variable.
    """
    value = os.getenv(env_var.value)
    if not value:
        if strict:
            logger.error("Missing required ENV var: '%s'", env_var)
            sys.exit(1)
        else:
            return None
    return value


def extract_text_between_brackets(text):
    match = re.search(r'\[([^\]]+)\]', text)
    if match:
        return match.group(1)
    else:
        return None


def main(args):

    input_dir = args.input_dir
    output_dir = args.output_dir
    dataset_metadata_path = args.dataset_metadata_path
    files_metadata_path = args.files_metadata_path

    if not input_dir or not output_dir or not dataset_metadata_path or not files_metadata_path:
        error_msg = "Set ROBOTO_INPUT_DIR, ROBOTO_OUTPUT_DIR and ROBOTO_DATASET_METADATA_CHANGESET_FILE, ROBOTO_FILE_METADATA_CHANGESET_FILE env variables."
        logger.error(error_msg)
        raise RuntimeError(error_msg)

    # get dataset id
    invocation_id = load_env_var(RobotoEnvKey.InvocationId, strict=False)
    logger.info(f"{invocation_id=}")

    # If inside an invocation, get info for file-level tagging
    if invocation_id:
        # Setup and authorize HTTP client
        client = HttpClient(default_auth=SigV4AuthDecorator("execute-api"))
        service_url = load_env_var(RobotoEnvKey.RobotoServiceUrl)

        delegate = http_delegates.HttpDelegates.from_client(http=client, endpoint=service_url)
        invocation = actions.invocation.Invocation.from_id(invocation_id, delegate.invocations)
        dataset_id = invocation.data_source.data_source_id
        logger.info(f"{dataset_id}=")
        transaction_manager = TransactionManager(service_url, client)

        dataset = datasets.dataset.Dataset.from_id(dataset_id, dataset_delegate=delegate.datasets,
                                                   file_delegate=delegate.files,
                                                   transaction_manager=transaction_manager)
    else:
        dataset = None

    for root, dirs, paths in os.walk(input_dir):
        for file in paths:
            # Check if the file ends with .ulg
            if file.endswith(".ulg"):
                _, ulg_file_name = os.path.split(file)
                msg_filter = []
                full_path = os.path.join(root, file)
                ulog = ULog(full_path, msg_filter, True)
                file_put_tags = list()
                for m in ulog.logged_messages:
                    print(m.log_level_str() + " " + m.message)
                    if m.log_level_str() == "ERROR":
                        module_name = extract_text_between_brackets(m.message)
                        if module_name is not None:
                            module_name = "ERROR_" + module_name
                            if module_name not in file_put_tags:
                                file_put_tags.append(module_name)
                        continue

                if dataset and file_put_tags:
                    for tag in file_put_tags:
                        # build a MetadataChangeset with put_tag direction
                        changeset = updates.MetadataChangeset().Builder().put_tag(tag).build()
                        ulg_file = dataset.get_file_info(file)
                        file_update_request = files.file_requests.UpdateFileRecordRequest(metadata_changeset=changeset)
                        # pass request to add metadata
                        ulg_file = ulg_file.update(file_update_request)
                        logger.info(f"Tagging {file} with {tag}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-i",
        "--input-dir",
        dest="input_dir",
        type=pathlib.Path,
        required=False,
        help="Directory containing input files to process",
        default=load_env_var(RobotoEnvKey.InputDir),
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        dest="output_dir",
        type=pathlib.Path,
        required=False,
        help="Directory to which to write any output files to be uploaded",
        default=load_env_var(RobotoEnvKey.OutputDir)
    )
    parser.add_argument(
        "-d",
        "--dataset-metadata-path",
        dest="dataset_metadata_path",
        type=pathlib.Path,
        required=False,
        help="Path at which to save dataset-level metadata",
        default=load_env_var(RobotoEnvKey.DatasetMetadataChangesetFile)
    )
    parser.add_argument(
        "-f",
        "--files-metadata-path",
        dest="files_metadata_path",
        type=pathlib.Path,
        required=False,
        help="Path at which to save file-level metadata",
        default=load_env_var(RobotoEnvKey.FileMetadataChangesetFile)
    )

    args = parser.parse_args()
    main(args)
