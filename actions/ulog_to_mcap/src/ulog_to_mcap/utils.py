import hashlib
import json
import os
from mcap.writer import Writer
from typing import Dict, List, Tuple, Any

from roboto.domain import actions

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


def create_per_topic_mcap_from_ulog(
    ulog: Any, output_folder_path: str
) -> Tuple[Dict[str, Any], Dict[str, str]]:
    """
    Creates per-topic MCAP files from a ULog object.

    Args:
    - ulog: ULog object containing log data.
    - output_folder_path: Path to the folder where the output MCAP files will be stored.

    Returns:
    - A tuple containing a schema registry dictionary and a schema checksum dictionary.
    """
    schema_registry_dict = {}
    schema_checksum_dict = {}

    for key in ulog.message_formats:
        json_schema_topic = create_json_schema(ulog.message_formats[key].fields)
        schema_registry_dict[key] = json_schema_topic
        schema_checksum_dict[key] = compute_checksum(json_schema_topic)

    for d in ulog.data_list:
        output_path_per_topic_mcap = os.path.join(output_folder_path, f"{d.name}.mcap")
        with open(output_path_per_topic_mcap, "wb") as stream:
            writer = Writer(stream)
            writer.start()

            schema_id = writer.register_schema(
                name=d.name,
                encoding="jsonschema",
                data=json.dumps(schema_registry_dict[d.name]).encode(),
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
                writer.add_message(
                    channel_id=channel_id,
                    log_time=int(d.data["timestamp"][i] * 1000),
                    data=json.dumps(json_msg_instance).encode("utf-8"),
                    publish_time=int(d.data["timestamp"][i] * 1000),
                )

            writer.finish()

    return schema_registry_dict, schema_checksum_dict


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
