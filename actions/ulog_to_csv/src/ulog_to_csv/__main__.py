import argparse
import os
import pathlib

from pyulog.ulog2csv import convert_ulog2csv
from roboto.domain import actions


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
parser.add_argument(
    "-d",
    "--delimiter",
    dest="delimiter",
    type=str,
    help="Delimiter used in output CSV file",
    default=os.environ.get("ROBOTO_PARAM_DELIMITER", ","),
)
parser.add_argument(
    "--time-start",
    dest="time_s",
    type=float,
    required=False,
    help="Start time for processing logs [s]",
    default=os.environ.get("ROBOTO_PARAM_TIME_START", None),
)
parser.add_argument(
    "--time-end",
    dest="time_e",
    type=float,
    required=False,
    help="End time for processing logs [s]",
    default=os.environ.get("ROBOTO_PARAM_TIME_END", None),
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
            convert_ulog2csv(
                ulog_file_name=full_path,
                messages=args.messages,
                output=output_folder_path,
                delimiter=args.delimiter,
                time_s=args.time_s,
                time_e=args.time_e,
            )
