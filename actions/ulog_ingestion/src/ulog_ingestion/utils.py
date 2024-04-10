import hashlib
from roboto.env import RobotoEnvKey
import pathlib
import os
import tempfile
import math
from mcap.writer import Writer
from typing import Dict, List, Tuple, Any
from roboto.domain import topics
import base64
from pyulog.core import ULog
import json


# Mapping from message definition types to JSON schema types
TYPE_MAPPING = {
    "int8_t": "integer",
    "uint8_t": "integer",
    "int16_t": "integer",
    "uint16_t": "integer",
    "int32_t": "integer",
    "uint32_t": "integer",
    "int64_t": "integer",
    "uint64_t": "integer",
    "float": "number",
    "double": "number",
    "bool": "boolean",
    "char": "string",
}


# Mapping from message definition types to Roboto canonical data types
TYPE_MAPPING_CANONICAL = {
    "int8_t": topics.CanonicalDataType.Number,
    "uint8_t": topics.CanonicalDataType.Number,
    "int16_t": topics.CanonicalDataType.Number,
    "uint16_t": topics.CanonicalDataType.Number,
    "int32_t": topics.CanonicalDataType.Number,
    "uint32_t": topics.CanonicalDataType.Number,
    "int64_t": topics.CanonicalDataType.Number,
    "uint64_t": topics.CanonicalDataType.Number,
    "float": topics.CanonicalDataType.Number,
    "double": topics.CanonicalDataType.Number,
    "bool": topics.CanonicalDataType.Boolean,
    "char": topics.CanonicalDataType.String,
}


def compute_checksum(json_schema: Dict[str, Any]) -> str:
    """
    Computes the SHA-256 checksum of a given JSON schema.

    This function serializes the JSON schema, sorts its keys for consistency,
    and then computes the SHA-256 checksum of the serialized data.

    Args:
    - json_schema: A dictionary representing the JSON schema.

    Returns:
    - The SHA-256 checksum of the serialized JSON schema as a hexadecimal string.
    """
    serialized_schema = json.dumps(json_schema, sort_keys=True).encode("utf-8")
    return hashlib.sha256(serialized_schema).hexdigest()


def create_json_schema(
    message_definition: List[Tuple[str, int, str]]
) -> Dict[str, Any]:
    """
    Creates a JSON schema based on a message definition.

    This function iterates over each field in the message definition and constructs
    a JSON schema. Fields starting with '_padding' are ignored. The function supports
    handling both array and non-array types.

    Args:
    - message_definition: A list of tuples, each representing a field in the message.
      Each tuple contains the field type, array size, and field name.

    Returns:
    - A dictionary representing the constructed JSON schema.
    """
    schema = {"type": "object", "properties": {}, "required": []}

    for field_type, array_size, field_name in message_definition:
        if field_name.startswith("_padding"):
            continue

        json_field_type = TYPE_MAPPING.get(field_type, "string")

        if array_size > 1:
            schema_property = {
                "type": "array",
                "items": {"type": json_field_type},
                "minItems": array_size,
                "maxItems": array_size,
            }
        else:
            schema_property = {"type": json_field_type}

        schema["properties"][field_name] = schema_property
        schema["required"].append(field_name)

    return schema


def parse_values_to_json(values: List[Tuple[str, str, Any]]) -> Dict[str, Any]:
    """
    Parses a list of field values into a JSON-compatible format.

    This function iterates over each tuple in the provided list, handling both
    array and non-array types. It constructs a JSON object based on field names,
    types, and values. Array fields are accumulated before being added to the JSON object.

    Args:
    - values: A list of tuples, each containing a field name, field type, and field value.

    Returns:
    - A dictionary representing the JSON object constructed from the input values.
    """
    json_instance = {}
    array_values = {}

    for field_name, field_type, field_value in values:

        if "[" in field_name:
            array_name = field_name.split("[")[0]
            array_values.setdefault(array_name, []).append(
                convert_value(field_type, field_value)
            )
        else:
            json_instance[field_name] = convert_value(field_type, field_value)

    json_instance.update(array_values)
    return json_instance


def convert_value(field_type: str, value: Any) -> Any:
    """
    Converts a field value to its corresponding JSON type.

    Args:
    - field_type: The type of the field as a string.
    - value: The value to be converted.

    Returns:
    - The converted value in its appropriate JSON type.
    """
    if math.isnan(value):
        return None

    json_type = TYPE_MAPPING.get(field_type, "string")
    if json_type == "integer":
        return int(value)
    elif json_type == "number":
        return float(value)
    elif json_type == "boolean":
        return bool(int(value))
    elif json_type == "string":
        return str(value)
    else:
        return value


def create_message_path_records(topic: Any, field_data: Any) -> None:
    """
    Creates message path records for a given topic.

    Args:
    - topic: The topic object to which the message paths will be added.
    - field_data: A list of field data objects containing the message definition.
    """
    array_list = list()
    for field in field_data:
        # For now only allow these types. TODO: Add support for nested types

        if field.type_str not in TYPE_MAPPING_CANONICAL.keys():
            canonical_data_type = topics.CanonicalDataType.Unknown
        else:
            canonical_data_type = TYPE_MAPPING_CANONICAL[field.type_str]

        if "[" in field.field_name:
            array_name = field.field_name.split("[")[0]
            array_field_type = f"{field.type_str}[]"

            if array_name not in array_list:
                topic.add_message_path(
                    request=topics.AddMessagePathRequest(
                        message_path=array_name,
                        data_type=array_field_type,  # TBD
                        canonical_data_type=topics.CanonicalDataType.Array,
                    )
                )

                print(
                    f"Adding array: {array_name}, type: {array_field_type}, canonical: {topics.CanonicalDataType.Array}"
                )

                # Add another message path for the array elements
                sub_array_name = f"{array_name}.[*]"
                topic.add_message_path(
                    request=topics.AddMessagePathRequest(
                        message_path=sub_array_name,
                        data_type=field.type_str,  # TBD
                        canonical_data_type=canonical_data_type,
                    )
                )

                print(
                    f"Adding sub-field for array: {sub_array_name}, type: {field.type_str}, canonical: {canonical_data_type}"
                )

                array_list.append(array_name)
        else:

            topic.add_message_path(
                request=topics.AddMessagePathRequest(
                    message_path=field.field_name,
                    data_type=field.type_str,
                    canonical_data_type=canonical_data_type,
                )
            )

            print(
                f"Adding field: {field.field_name}, type: {field.type_str}, canonical: {canonical_data_type}"
            )
    return


def generate_config(file_id, relative_path):
    viz_config = {
        "version": "v1",
        "files": [{"fileId": file_id, "relativePath": relative_path}],
    }
    return base64.urlsafe_b64encode(json.dumps(viz_config).encode("utf-8")).decode(
        "utf-8"
    )


def create_per_topic_mcap_from_ulog(
    output_path_per_topic_mcap: Any, d: str, json_schema_topic: Any
) -> None:
    """
    Creates a per-topic MCAP file from a ULog object.

    Args:
    - output_path_per_topic_mcap: The path to the output MCAP file.
    - d: The ULog object containing the data to be converted.
    - json_schema_topic: The json schema dict for the topic.

    Returns:
    - None
    """

    with open(output_path_per_topic_mcap, "wb") as stream:
        writer = Writer(stream)
        writer.start()
        schema_id = writer.register_schema(
            name=d.name,
            encoding="jsonschema",
            data=json.dumps(json_schema_topic).encode(),
        )

        channel_id = writer.register_channel(
            schema_id=schema_id,
            topic=d.name,
            message_encoding="json",
        )

        for i in range(len(d.data["timestamp"])):
            values = list()
            for f in d.field_data:
                values.append((f.field_name, f.type_str, d.data[f.field_name][i]))

            json_msg_instance = parse_values_to_json(values)

            timestamp_ns = int(d.data["timestamp"][i] * 1000)

            writer.add_message(
                channel_id=channel_id,
                log_time=timestamp_ns,
                sequence=i,
                data=json.dumps(json_msg_instance).encode("utf-8"),
                publish_time=timestamp_ns,
            )

        writer.finish()
    return


def setup_output_folder_structure(
    ulog_file_path: str, input_dir: str
) -> Tuple[str, str]:
    """
    Set up the output folder structure for the .mcap files.

    Args:
    - ulog_file_path: Path to the .ulg file.
    - input_dir: Path to the input directory.
    """
    relative_folder_path_of_file = os.path.split(ulog_file_path.split(input_dir)[1])[0]

    ulog_file_name = os.path.split(ulog_file_path)[1]

    output_folder_name_ulog = ulog_file_name.replace(".ulg", "")
    relative_folder_path_of_file = relative_folder_path_of_file.lstrip("/")
    temp_dir = str(tempfile.TemporaryDirectory().name)

    output_folder_path = os.path.join(
        temp_dir,
        ".VISUALIZATION_ASSETS",
        relative_folder_path_of_file,
        output_folder_name_ulog,
    )

    print(f"Output folder path: {output_folder_path}")
    os.makedirs(output_folder_path, exist_ok=True)

    return output_folder_path, temp_dir


def is_valid_ulog(ulog_file_path: str) -> bool:
    """
    Check if the given file is a valid .ulg file.

    Args:
    - ulog_file_path: Path to the .ulg file.

    Returns:
    - True if the file is a valid .ulg file, False otherwise.
    """

    header_bytes = b'\x55\x4c\x6f\x67\x01\x12\x35'

    with open(ulog_file_path, "rb") as file_handle:

        header_data = file_handle.read(16)
        if len(header_data) != 16:
            raise TypeError("Invalid ULog file format (Header too short)")
        if header_data[:7] != header_bytes:
            raise TypeError("Invalid ULog file format (Failed to parse header)")

        return True


# Helper function. Will be deleted.
def generate_config(file_id, relative_path):
    viz_config = {
        "version": "v1",
        "files": [{"fileId": file_id, "relativePath": relative_path}],
    }
    return base64.urlsafe_b64encode(json.dumps(viz_config).encode("utf-8")).decode(
        "utf-8"
    )


def add_metadata_to_file(ulog_file_path: str, topics: List[str] = None):

    msg_filter = topics.split(",") if topics else None
    ulog = ULog(ulog_file_path, msg_filter, True)

    input_dir = os.environ[f"{RobotoEnvKey.InputDir.value}"]
    relative_file_name = ulog_file_path.split(input_dir)[1][1:]

    file_metadata_changeset_file_path = os.environ[f"{RobotoEnvKey.FileMetadataChangesetFile.value}"]
    file_metadata_changeset_file = pathlib.Path(file_metadata_changeset_file_path)

    json_line = json.dumps(
        {
            "relative_path": relative_file_name,
            "update": {
                "metadata_changeset": {
                    "put_fields": ulog.msg_info_dict,
                },
                "description": "",
            },
        }
    )

    with file_metadata_changeset_file.open('a') as file:
        if file.tell() > 0:
            file.write('\n')
        file.write(json_line)
