from pyulog.core import ULog
import os
import re
from pathlib import Path

import logging
from roboto import ActionRuntime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_text_between_brackets(text):
    '''
    Extract text between brackets

    Args:
        text (str): Text to extract from

    Returns:
        str: Text between brackets
    '''

    match = re.search(r'\[([^\]]+)\]', text)
    if match:
        return match.group(1)
    else:
        return None


if __name__ == "__main__":
    runtime = ActionRuntime.from_env()

    input_dir = runtime.input_dir
    output_dir = runtime.output_dir
    dataset = runtime.dataset

    if not input_dir:
        error_msg = "Set ROBOTO_INPUT_DIR env variable."
        logger.error(error_msg)
        raise RuntimeError(error_msg)

    for root, dirs, paths in os.walk(input_dir):
        for file in paths:
            # Check if the file ends with .ulg
            if file.endswith(".ulg"):
                _, ulg_file_name = os.path.split(file)

                msg_filter = []
                full_path = os.path.join(root, file)
                relative_path = Path(full_path).relative_to(input_dir)
                file_id = dataset.get_file_by_path(relative_path)

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
                file_id.put_tags(tags=file_put_tags)