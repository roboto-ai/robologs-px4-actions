#! /usr/bin/env python
"""
Display information from an ULog file to a Markdown file
"""

from __future__ import print_function

import argparse
import os.path

from pyulog.core import ULog

#pylint: disable=too-many-locals, unused-wildcard-import, wildcard-import
#pylint: disable=invalid-name


def show_info(ulog_file_path, output_folder, verbose, ignore_str_exceptions, hidden):
    """Show general information from an ULog"""

    ulog = ULog(ulog_file_path, None, ignore_str_exceptions)

    _, ulg_file_name = os.path.split(ulog_file_path)

    md_file_name = ulg_file_name.replace('.ulg', '.md')

    if hidden:
        md_file_name = '.' + md_file_name

    md_file_path = os.path.join(output_folder, md_file_name)

    print("Writing to {}".format(md_file_path))

    m1, s1 = divmod(int(ulog.start_timestamp/1e6), 60)
    h1, m1 = divmod(m1, 60)
    m2, s2 = divmod(int((ulog.last_timestamp - ulog.start_timestamp)/1e6), 60)
    h2, m2 = divmod(m2, 60)

    with open(md_file_path, 'w') as md_file:

        md_file.write("# ULog Information\n\n")
        md_file.write("## Logging start time\n")
        md_file.write("`Logging start time: {:d}:{:02d}:{:02d}, duration: {:d}:{:02d}:{:02d}`\n\n".format(
            h1, m1, s1, h2, m2, s2))

        dropout_durations = [dropout.duration for dropout in ulog.dropouts]
        if len(dropout_durations) == 0:
            md_file.write("No Dropouts\n")
        else:
            md_file.write("## Dropouts\n")
            md_file.write("`Dropouts: count: {:}, total duration: {:.1f} s, max: {:} ms, mean: {:} ms`\n\n"
                  .format(len(dropout_durations), sum(dropout_durations)/1000.,
                          max(dropout_durations),
                          int(sum(dropout_durations)/len(dropout_durations))))

        version = ulog.get_version_info_str()
        if not version is None:
            md_file.write('## SW Version\n')
            md_file.write("`SW Version: {}`\n\n".format(version))

        md_file.write("## Info Messages\n")
        for k in sorted(ulog.msg_info_dict):
            if not k.startswith('perf_') or verbose:
                md_file.write("- **{}**: {}\n".format(k, ulog.msg_info_dict[k]))
        md_file.write("\n")

        if len(ulog.msg_info_multiple_dict) > 0:
            if verbose:
                md_file.write("## Info Multiple Messages (Verbose)\n")
                for k in sorted(ulog.msg_info_multiple_dict):
                    md_file.write("- **{}**: {}\n".format(k, ulog.msg_info_multiple_dict[k]))
                md_file.write("\n")
            else:
                md_file.write("## Info Multiple Messages\n")
                md_file.write("- {}\n".format(", ".join(["**{}**: {}".format(k, len(ulog.msg_info_multiple_dict[k])) for k in
                               sorted(ulog.msg_info_multiple_dict)])))
                md_file.write("\n")

        md_file.write("## Data Points Information\n")
        md_file.write("| Name (multi id, message size in bytes) | number of data points | total bytes |\n")
        md_file.write("| --- | --- | --- |\n")

        data_list_sorted = sorted(ulog.data_list, key=lambda d: d.name + str(d.multi_id))
        for d in data_list_sorted:
            message_size = sum(ULog.get_field_size(f.type_str) for f in d.field_data)
            num_data_points = len(d.data['timestamp'])
            name_id = "{} ({}, {})".format(d.name, d.multi_id, message_size)
            md_file.write("| {} | {} | {} |\n".format(name_id, num_data_points,
                                                message_size * num_data_points))
        md_file.write("\n")


def main():
    """Commande line interface"""
    parser = argparse.ArgumentParser(description='Display information from an ULog file')
    parser.add_argument('filename', metavar='file.ulg', help='ULog input file')
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true',
                        help='Verbose output', default=False)
    parser.add_argument('-m', '--message', dest='message',
                        help='Show a specific Info Multiple Message')
    parser.add_argument('-n', '--newline', dest='newline', action='store_true',
                        help='Add newline separators (only with --message)', default=False)
    parser.add_argument('-i', '--ignore', dest='ignore', action='store_true',
                        help='Ignore string parsing exceptions', default=False)

    args = parser.parse_args()
    ulog_file_name = args.filename
    disable_str_exceptions = args.ignore

    show_info(ulog_file_name,
              output_folder="./",
              verbose=False,
              ignore_str_exceptions=True,
              hidden=False)
main()

