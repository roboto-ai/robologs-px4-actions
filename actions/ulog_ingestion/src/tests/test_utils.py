import os.path
import shutil
import ulog_ingestion.utils as utils
from pyulog.core import ULog


def test_create_mcap_file_from_ulog(tmp_path):
    ulog_file_path = "./tests/test.ulg"

    test_topic_name = "vehicle_acceleration"

    output_path_per_topic_mcap = tmp_path / f"{test_topic_name}.mcap"

    ulog = ULog(ulog_file_path, [test_topic_name], True)

    schema_registry_dict = {}

    for key in ulog.message_formats:
        json_schema_topic = utils.create_json_schema(ulog.message_formats[key].fields)
        schema_registry_dict[key] = json_schema_topic

    for data_object in sorted(ulog.data_list, key=lambda obj: obj.name):
        print(data_object.name)
        utils.create_per_topic_mcap_from_ulog(output_path_per_topic_mcap,
                                              data_object,
                                              schema_registry_dict[data_object.name])

    assert output_path_per_topic_mcap.exists()


def test_setup_output_folder_structure():

    ulog_file_path = "/workspace/abc/test.ulg"
    input_dir = "/workspace/"

    output_folder_path, temp_dir = utils.setup_output_folder_structure(ulog_file_path, input_dir)

    assert output_folder_path == f"{temp_dir}/.VISUALIZATION_ASSETS/abc/test"
    assert os.path.exists(output_folder_path)
    shutil.rmtree(output_folder_path)


def test_is_valid_ulog():

    ulog_file_path = "./tests/test.ulg"
    is_valid = utils.is_valid_ulog(ulog_file_path)
    assert is_valid is True


# def test_add_metadata():
#     ulog_file_path = "./tests/test.ulg"
#     #topics = ["vehicle_acceleration"]
#
#     utils.add_metadata(ulog_file_path, topics=None)

    # assert os.path.exists(ulog_file_path)
    # assert os.path.exists(f"{ulog_file_path}.metadata.json")
    # os.remove(f"{ulog_file_path}.metadata.json")
    # assert not os.path.exists(f"{ulog_file_path}.metadata.json")
