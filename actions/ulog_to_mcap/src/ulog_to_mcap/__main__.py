import argparse
import os
import pathlib
from typing import List
from pyulog.core import ULog
import json
from time import time_ns

from mcap.writer import Writer
from roboto.domain import actions
from ulog_to_mcap.utils import create_json_schema, parse_values_to_json


def convert_ulog_to_mcap(ulog_file_path: str,
                         output_folder_path: str,
                         messages: List[str] = None):
    """
    Convert a ULog file to a MCAP file.
    """
    msg_filter = messages.split(',') if messages else None
    disable_str_exceptions = True
    print(ulog_file_path)

    schema_registry = {}

    # Create schema registry
    ulog = ULog(ulog_file_path, msg_filter, disable_str_exceptions)

    for key in ulog.message_formats:
        json_schema_topic = create_json_schema(ulog.message_formats[key].fields)
        schema_registry[key] = json_schema_topic

    data = ulog.data_list
    for d in data:

        with open(os.path.join(output_folder_path, f"{d.name}.mcap"), "wb") as stream:
            writer = Writer(stream)

            writer.start()

            schema_id = writer.register_schema(
                name="sample",
                encoding="jsonschema",
                data=json.dumps(schema_registry[d.name]).encode(),
            )

            channel_id = writer.register_channel(
                schema_id=schema_id,
                topic=d.name,
                message_encoding="json",
            )

            for i in range(len(d.data['timestamp'])):
                values = list()
                for f in d.field_data:
                    values.append((f.field_name, f.type_str, d.data[f.field_name][i]))
                print(values)
                json_msg_instance = parse_values_to_json(values)
                print(json_msg_instance)
                # print(type(json_msg_instance))
                # for k in json_msg_instance.keys():
                #     print(k, type(json_msg_instance[k]))
                #     print(json_msg_instance["key"][0])

                writer.add_message(
                    channel_id=channel_id,
                    log_time=time_ns(),
                    data=json.dumps(json_msg_instance).encode("utf-8"),
                    publish_time=time_ns(),
                )

            writer.finish()


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

for root, dirs, files in os.walk(args.input_dir):
    for file in files:
        # Check if the file ends with .ulg
        if file.endswith(".ulg"):
            _, ulg_file_name = os.path.split(file)
            ulg_output_folder_name = ulg_file_name.replace(".ulg", "")
            output_folder_path = os.path.join(args.output_dir, ulg_output_folder_name)

            if not os.path.exists(output_folder_path):
                os.makedirs(output_folder_path, exist_ok=True)

            full_path = os.path.join(root, file)
            convert_ulog_to_mcap(ulog_file_path=full_path,
                                 output_folder_path=output_folder_path,
                                 messages=args.messages)


