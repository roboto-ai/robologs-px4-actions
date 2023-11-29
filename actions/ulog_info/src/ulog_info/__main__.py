import argparse
import os
import pathlib
import os.path

from pyulog.core import ULog
from roboto.domain import actions


def process_ulg_files(
    input_folder, output_folder, verbose, ignore_str_exceptions, hidden
):
    """
    Process all .ulg files within a given folder and its subdirectories.

    Args:
        input_folder (pathlib.Path): The folder containing .ulg files.
        output_folder (pathlib.Path): The folder to store the output files.
        verbose (bool): Flag for verbose logging.
        ignore_str_exceptions (bool): Flag to ignore string exceptions.
        hidden (bool): Flag to determine if output files should be hidden.
    """
    for root, dirs, files in os.walk(input_folder):
        for file in files:
            # Check if the file ends with .ulg
            if file.endswith(".ulg"):
                full_path = os.path.join(root, file)
                show_info(
                    ulog_file_path=full_path,
                    output_folder=output_folder,
                    verbose=verbose,
                    ignore_str_exceptions=ignore_str_exceptions,
                    hidden=hidden,
                )


def show_info(ulog_file_path, output_folder, verbose, ignore_str_exceptions, hidden):
    """
    Show general information from a ULog file and write it to a markdown file.

    Args:
        ulog_file_path (str): Path to the .ulg file.
        output_folder (pathlib.Path): Folder to store the markdown file.
        verbose (bool): Flag for verbose logging.
        ignore_str_exceptions (bool): Flag to ignore string exceptions.
        hidden (bool): Flag to determine if the markdown file should be hidden.
    """

    ulog = ULog(ulog_file_path, None, ignore_str_exceptions)

    _, ulg_file_name = os.path.split(ulog_file_path)

    md_file_name = ulg_file_name + ".md"

    if hidden:
        md_file_name = "." + md_file_name

    md_file_path = os.path.join(output_folder, md_file_name)

    print("Writing to {}".format(md_file_path))

    m1, s1 = divmod(int(ulog.start_timestamp / 1e6), 60)
    h1, m1 = divmod(m1, 60)
    m2, s2 = divmod(int((ulog.last_timestamp - ulog.start_timestamp) / 1e6), 60)
    h2, m2 = divmod(m2, 60)

    with open(md_file_path, "w") as md_file:

        md_file.write("# ULog Information\n\n")
        md_file.write("## Logging start time\n")
        md_file.write(
            "`Logging start time: {:d}:{:02d}:{:02d}, duration: {:d}:{:02d}:{:02d}`\n\n".format(
                h1, m1, s1, h2, m2, s2
            )
        )

        dropout_durations = [dropout.duration for dropout in ulog.dropouts]
        if len(dropout_durations) == 0:
            md_file.write("No Dropouts\n")
        else:
            md_file.write("## Dropouts\n")
            md_file.write(
                "`Dropouts: count: {:}, total duration: {:.1f} s, max: {:} ms, mean: {:} ms`\n\n".format(
                    len(dropout_durations),
                    sum(dropout_durations) / 1000.0,
                    max(dropout_durations),
                    int(sum(dropout_durations) / len(dropout_durations)),
                )
            )

        version = ulog.get_version_info_str()
        if not version is None:
            md_file.write("## SW Version\n")
            md_file.write("`SW Version: {}`\n\n".format(version))

        md_file.write("## Info Messages\n")
        for k in sorted(ulog.msg_info_dict):
            if not k.startswith("perf_") or verbose:
                md_file.write("- **{}**: {}\n".format(k, ulog.msg_info_dict[k]))
        md_file.write("\n")

        if len(ulog.msg_info_multiple_dict) > 0:
            if verbose:
                md_file.write("## Info Multiple Messages (Verbose)\n")
                for k in sorted(ulog.msg_info_multiple_dict):
                    md_file.write(
                        "- **{}**: {}\n".format(k, ulog.msg_info_multiple_dict[k])
                    )
                md_file.write("\n")
            else:
                md_file.write("## Info Multiple Messages\n")
                md_file.write(
                    "- {}\n".format(
                        ", ".join(
                            [
                                "**{}**: {}".format(
                                    k, len(ulog.msg_info_multiple_dict[k])
                                )
                                for k in sorted(ulog.msg_info_multiple_dict)
                            ]
                        )
                    )
                )
                md_file.write("\n")

        md_file.write("## Data Points Information\n")
        md_file.write(
            "| Name (multi id, message size in bytes) | number of data points | total bytes |\n"
        )
        md_file.write("| --- | --- | --- |\n")

        data_list_sorted = sorted(
            ulog.data_list, key=lambda d: d.name + str(d.multi_id)
        )
        for d in data_list_sorted:
            message_size = sum(ULog.get_field_size(f.type_str) for f in d.field_data)
            num_data_points = len(d.data["timestamp"])
            name_id = "{} ({}, {})".format(d.name, d.multi_id, message_size)
            md_file.write(
                "| {} | {} | {} |\n".format(
                    name_id, num_data_points, message_size * num_data_points
                )
            )
        md_file.write("\n")


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
    "-d",
    "--hidden",
    action="store_true",
    required=False,
    help="Output hidden markdown files with '.' prefix",
    default=(os.environ.get("ROBOTO_PARAM_HIDDEN") == "True"),
)

args = parser.parse_args()
process_ulg_files(args.input_dir, args.output_dir, False, True, args.hidden)
