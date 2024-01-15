# Type mapping from message definition types to JSON schema types
type_mapping = {
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
    "char": "string"
}


def create_json_schema(message_definition):
    # JSON schema template
    schema = {
        "type": "object",
        "properties": {},
        "required": []
    }

    # Iterate over each field in the new message definition format
    for field_type, array_size, field_name in message_definition:
        if field_name.startswith('_padding'):
            continue

        json_field_type = type_mapping.get(field_type, "string")  # Default to string if type not mapped

        if array_size > 1:
            # Handle array types
            schema_property = {
                "type": "array",
                "items": {"type": json_field_type},
                "minItems": array_size,
                "maxItems": array_size
            }
        else:
            # Handle non-array types
            schema_property = {"type": json_field_type}

        schema["properties"][field_name] = schema_property
        schema["required"].append(field_name)

    return schema


def parse_values_to_json(values):
    # Initialize an empty JSON object
    json_instance = {}

    # Temporary storage for array values
    array_values = {}

    # Process each tuple in the list
    for field_name, field_type, field_value in values:
        if '[' in field_name:
            # Handle array types
            array_name = field_name.split('[')[0]
            if array_name not in array_values:
                array_values[array_name] = []
            array_values[array_name].append(convert_value(field_type, field_value))
            print(field_type)
        else:
            # Convert the value and add to the JSON instance
            json_instance[field_name] = convert_value(field_type, field_value)

    # Add array values to the JSON instance
    for array_name, array_vals in array_values.items():
        json_instance[array_name] = array_vals

    return json_instance


def convert_value(field_type, value):

    json_type = type_mapping.get(field_type)

    if json_type == "integer":
        return int(value)
    elif json_type == "number":
        return float(value)
    elif json_type == "boolean":
        return bool(int(value))  # assuming boolean values are represented as 0 or 1
    else:
        return value  # This includes the 'string' type and any other type not explicitly mapped