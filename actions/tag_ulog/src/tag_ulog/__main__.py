from pyulog.core import ULog
from roboto.domain import actions

import argparse
import logging
import os
import pathlib
import json
import re
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_text_between_brackets(text):
    match = re.search(r'\[([^\]]+)\]', text)
    if match:
        return match.group(1)
    else:
        return None


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


args = parser.parse_args()

output_path_metadata = os.getenv("ROBOTO_DATASET_METADATA_CHANGESET_FILE", "/output/changeset.json")

put_tags = list()

put_fields = dict()

for root, dirs, files in os.walk(args.input_dir):
    for file in files:
        # Check if the file ends with .ulg
        if file.endswith(".ulg"):
            _, ulg_file_name = os.path.split(file)
            msg_filter = []
            full_path = os.path.join(root, file)
            ulog = ULog(full_path, msg_filter, True)
            for m in ulog.logged_messages:
                if m.log_level_str() == "ERROR":
                    module_name = extract_text_between_brackets(m.message)
                    if module_name is not None:
                        module_name = "ERROR_" + module_name
                        if module_name not in put_tags:
                            put_tags.append(module_name)
                    continue
                print(f"{m.log_level_str()} {m.message}")

    with open(output_path_metadata, "w") as json_file:
        metadata_dict = {
            "put_tags": list(set(put_tags)),
            "remove_tags": [],
            "put_fields": put_fields,
            "remove_fields": [],
        }
        logger.info(f"Writing {output_path_metadata}...")
        json.dump(metadata_dict, json_file, indent=4)
