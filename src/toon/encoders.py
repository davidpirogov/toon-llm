"""
Encoders module for converting JSON-like Python data structures to custom text format.

This module provides encoding functions for different data types including primitives,
objects (dicts), and arrays (lists) with support for various formatting strategies.

Encoding strategies:
- Primitive values: strings, numbers, booleans, null
- Objects (dicts): key-value pairs with nested structures
- Arrays (lists):
  - Inline format for primitive arrays
  - Tabular format for uniform arrays of objects
  - Expanded list format for mixed/nested arrays
"""

from typing import Literal, Optional, Sequence, Union

from toon.constants import LIST_ITEM_PREFIX
from toon.normalize import (
    is_array_of_arrays,
    is_array_of_objects,
    is_array_of_primitives,
    is_json_array,
    is_json_object,
    is_json_primitive,
)
from toon.primitives import (
    encode_key,
    encode_primitive,
    format_header,
    join_encoded_values,
)
from toon.types import (
    Depth,
    JsonArray,
    JsonObject,
    JsonPrimitive,
    JsonValue,
    ResolvedEncodeOptions,
)
from toon.writer import LineWriter


def _check_type(
    value: object, expected_types: Union[type, tuple], type_name: str
) -> None:
    """
    Check that a value is an instance of expected types.

    Args:
        value: The value to check
        expected_types: Type or tuple of expected types
        type_name: Name of the expected type for error message

    Raises:
        ValueError: If the value is not of the expected type
    """
    if not isinstance(value, expected_types):
        actual_type = type(value).__name__
        raise ValueError(f"Expected {type_name}, got {actual_type}")


def encode_value(value: JsonValue, options: ResolvedEncodeOptions) -> str:
    """
    Encode a JSON-like value to the custom text format.

    Args:
        value: The JSON value to encode (primitive, array, or object)
        options: Encoding options including delimiter and indentation

    Returns:
        The encoded string representation
    """
    if is_json_primitive(value):
        # Type guard ensures value is JsonPrimitive here
        _check_type(value, (str, int, float, bool, type(None)), "JsonPrimitive")
        return encode_primitive(value, options.delimiter, options.quote)

    writer = LineWriter(options.indent)

    if is_json_array(value):
        _check_type(value, list, "JsonArray")
        encode_array(None, value, writer, 0, options)
    elif is_json_object(value):
        _check_type(value, dict, "JsonObject")
        encode_object(value, writer, 0, options)

    return writer.to_string()


def encode_object(
    value: JsonObject, writer: LineWriter, depth: Depth, options: ResolvedEncodeOptions
) -> None:
    """
    Encode a JSON object (dict) to the output writer.

    Args:
        value: The object to encode
        writer: The line writer for output
        depth: Current indentation depth
        options: Encoding options
    """
    keys = list(value.keys())

    for key in keys:
        # Convert non-string keys to strings
        key_str = str(key) if not isinstance(key, str) else key
        encode_key_value_pair(key_str, value[key], writer, depth, options)


def encode_key_value_pair(
    key: str,
    value: JsonValue,
    writer: LineWriter,
    depth: Depth,
    options: ResolvedEncodeOptions,
) -> None:
    """
    Encode a single key-value pair.

    Args:
        key: The key string
        value: The value to encode
        writer: The line writer for output
        depth: Current indentation depth
        options: Encoding options
    """
    encoded_key = encode_key(key)

    if is_json_primitive(value):
        _check_type(value, (str, int, float, bool, type(None)), "JsonPrimitive")
        writer.push(
            depth, f"{encoded_key}: {encode_primitive(value, options.delimiter, options.quote)}"
        )
    elif is_json_array(value):
        _check_type(value, list, "JsonArray")
        encode_array(key, value, writer, depth, options)
    elif is_json_object(value):
        _check_type(value, dict, "JsonObject")
        nested_keys = list(value.keys())
        if len(nested_keys) == 0:
            # Empty object
            writer.push(depth, f"{encoded_key}:")
        else:
            writer.push(depth, f"{encoded_key}:")
            encode_object(value, writer, depth + 1, options)


def encode_array(
    key: Optional[str],
    value: JsonArray,
    writer: LineWriter,
    depth: Depth,
    options: ResolvedEncodeOptions,
) -> None:
    """
    Encode a JSON array with automatic format detection.

    Args:
        key: Optional key for the array
        value: The array to encode
        writer: The line writer for output
        depth: Current indentation depth
        options: Encoding options
    """
    if len(value) == 0:
        header = format_header(
            0, key=key, delimiter=options.delimiter, length_marker=options.length_marker
        )
        writer.push(depth, header)
        return

    # Primitive array
    if is_array_of_primitives(value):
        encode_inline_primitive_array(key, value, writer, depth, options)
        return

    # Array of arrays (all primitives)
    if is_array_of_arrays(value):
        all_primitive_arrays = all(is_array_of_primitives(arr) for arr in value)
        if all_primitive_arrays:
            encode_array_of_arrays_as_list_items(key, value, writer, depth, options)
            return

    # Array of objects
    if is_array_of_objects(value):  # type: ignore[arg-type]
        header = detect_tabular_header(value)
        if header:
            encode_array_of_objects_as_tabular(
                key, value, header, writer, depth, options
            )
        else:
            encode_mixed_array_as_list_items(key, value, writer, depth, options)
        return

    # Mixed array: fallback to expanded format
    encode_mixed_array_as_list_items(key, value, writer, depth, options)


def encode_inline_primitive_array(
    prefix: Optional[str],
    values: Sequence[JsonPrimitive],
    writer: LineWriter,
    depth: Depth,
    options: ResolvedEncodeOptions,
) -> None:
    """
    Encode an array of primitives in inline format.

    Args:
        prefix: Optional prefix (key) for the array
        values: The primitive values to encode
        writer: The line writer for output
        depth: Current indentation depth
        options: Encoding options
    """
    formatted = format_inline_array(
        values, options.delimiter, options.quote, prefix, options.length_marker
    )
    writer.push(depth, formatted)


def format_inline_array(
    values: Sequence[JsonPrimitive],
    delimiter: str,
    quote: str,
    prefix: Optional[str] = None,
    length_marker: Literal["#", False] = False,
) -> str:
    """
    Format an inline array as a string.

    Args:
        values: The primitive values to format
        delimiter: The delimiter to use between values
        prefix: Optional prefix (key) for the array
        length_marker: The length marker to use or False to disable

    Returns:
        The formatted inline array string
    """
    if length_marker not in ["#", False]:
        raise ValueError(
            f"Expected Length Marker to be one of ['#', False], got {length_marker} (type: {type(length_marker)})"
        )

    header = format_header(
        len(values), key=prefix, delimiter=delimiter, length_marker=length_marker
    )
    joined_value = join_encoded_values(values, delimiter, quote)
    # Only add space if there are values
    if len(values) == 0:
        return header
    return f"{header} {joined_value}"


def encode_array_of_arrays_as_list_items(
    prefix: Optional[str],
    values: Sequence[JsonArray],
    writer: LineWriter,
    depth: Depth,
    options: ResolvedEncodeOptions,
) -> None:
    """
    Encode an array of arrays in list item format.

    Args:
        prefix: Optional prefix (key) for the array
        values: The arrays to encode
        writer: The line writer for output
        depth: Current indentation depth
        options: Encoding options
    """
    header = format_header(
        len(values),
        key=prefix,
        delimiter=options.delimiter,
        length_marker=options.length_marker,
    )
    writer.push(depth, header)

    for arr in values:
        if is_array_of_primitives(arr):
            inline = format_inline_array(
                arr, options.delimiter, options.quote, None, options.length_marker
            )
            writer.push(depth + 1, f"{LIST_ITEM_PREFIX}{inline}")


def encode_array_of_objects_as_tabular(
    prefix: Optional[str],
    rows: Sequence[JsonObject],
    header: Sequence[str],
    writer: LineWriter,
    depth: Depth,
    options: ResolvedEncodeOptions,
) -> None:
    """
    Encode an array of objects in tabular format.

    Args:
        prefix: Optional prefix (key) for the array
        rows: The objects to encode as rows
        header: The column headers (keys)
        writer: The line writer for output
        depth: Current indentation depth
        options: Encoding options
    """
    header_str = format_header(
        len(rows),
        key=prefix,
        fields=header,
        delimiter=options.delimiter,
        length_marker=options.length_marker,
    )
    writer.push(depth, header_str)

    write_tabular_rows(rows, header, writer, depth + 1, options)


def detect_tabular_header(rows: Sequence[JsonObject]) -> Optional[list[str]]:
    """
    Detect if an array of objects can be encoded in tabular format.

    Args:
        rows: The objects to check

    Returns:
        The header keys if tabular format is suitable, None otherwise
    """
    if len(rows) == 0:
        return None

    first_row = rows[0]
    first_keys = list(first_row.keys())
    if len(first_keys) == 0:
        return None

    if is_tabular_array(rows, first_keys):
        return first_keys

    return None


def is_tabular_array(rows: Sequence[JsonObject], header: Sequence[str]) -> bool:
    """
    Check if an array of objects is suitable for tabular format.

    All objects must have the same keys and all values must be primitives.

    Args:
        rows: The objects to check
        header: The expected header keys

    Returns:
        True if tabular format is suitable, False otherwise
    """
    for row in rows:
        keys = list(row.keys())

        # All objects must have the same keys (but order can differ)
        if len(keys) != len(header):
            return False

        # Check that all header keys exist in the row and all values are primitives
        for key in header:
            if key not in row:
                return False
            if not is_json_primitive(row[key]):
                return False

    return True


def write_tabular_rows(
    rows: Sequence[JsonObject],
    header: Sequence[str],
    writer: LineWriter,
    depth: Depth,
    options: ResolvedEncodeOptions,
) -> None:
    """
    Write tabular rows to the output.

    Args:
        rows: The objects to write as rows
        header: The column headers (keys)
        writer: The line writer for output
        depth: Current indentation depth
        options: Encoding options
    """
    for row in rows:
        values: list[JsonPrimitive] = [row[key] for key in header]  # type: ignore[misc]
        joined_value = join_encoded_values(values, options.delimiter, options.quote)
        writer.push(depth, joined_value)


def encode_mixed_array_as_list_items(
    prefix: Optional[str],
    items: Sequence[JsonValue],
    writer: LineWriter,
    depth: Depth,
    options: ResolvedEncodeOptions,
) -> None:
    """
    Encode a mixed array in list item format.

    Args:
        prefix: Optional prefix (key) for the array
        items: The items to encode
        writer: The line writer for output
        depth: Current indentation depth
        options: Encoding options
    """
    header = format_header(
        len(items),
        key=prefix,
        delimiter=options.delimiter,
        length_marker=options.length_marker,
    )
    writer.push(depth, header)

    for item in items:
        if is_json_primitive(item):
            # Direct primitive as list item
            _check_type(item, (str, int, float, bool, type(None)), "JsonPrimitive")
            writer.push(
                depth + 1,
                f"{LIST_ITEM_PREFIX}{encode_primitive(item, options.delimiter, options.quote)}",
            )
        elif is_json_array(item):
            # Direct array as list item
            _check_type(item, list, "JsonArray")
            if is_array_of_primitives(item):
                inline = format_inline_array(
                    item, options.delimiter, options.quote, None, options.length_marker
                )
                writer.push(depth + 1, f"{LIST_ITEM_PREFIX}{inline}")
        elif is_json_object(item):
            # Object as list item
            _check_type(item, dict, "JsonObject")
            encode_object_as_list_item(item, writer, depth + 1, options)


def encode_object_as_list_item(
    obj: JsonObject, writer: LineWriter, depth: Depth, options: ResolvedEncodeOptions
) -> None:
    """
    Encode an object as a list item with special formatting.

    The first key-value pair appears on the same line as the list marker,
    and remaining key-value pairs are indented.

    Args:
        obj: The object to encode
        writer: The line writer for output
        depth: Current indentation depth
        options: Encoding options
    """
    keys = list(obj.keys())
    if len(keys) == 0:
        writer.push(
            depth, "- "
        )  # Empty object in list format uses "- " for consistency
        return

    # First key-value on the same line as "- "
    first_key = keys[0]
    first_key_str = str(first_key) if not isinstance(first_key, str) else first_key
    encoded_key = encode_key(first_key_str)
    first_value = obj[first_key]

    if is_json_primitive(first_value):
        writer.push(
            depth,
            f"{LIST_ITEM_PREFIX}{encoded_key}: {encode_primitive(first_value, options.delimiter, options.quote)}",
        )
    elif is_json_array(first_value):
        if is_array_of_primitives(first_value):
            # Inline format for primitive arrays
            formatted = format_inline_array(
                first_value, options.delimiter, options.quote, first_key_str, options.length_marker
            )
            writer.push(depth, f"{LIST_ITEM_PREFIX}{formatted}")
        elif is_array_of_objects(first_value):
            # Check if array of objects can use tabular format
            header = detect_tabular_header(first_value)
            if header:
                # Tabular format for uniform arrays of objects
                header_str = format_header(
                    len(first_value),
                    key=first_key_str,
                    fields=header,
                    delimiter=options.delimiter,
                    length_marker=options.length_marker,
                )
                writer.push(depth, f"{LIST_ITEM_PREFIX}{header_str}")
                write_tabular_rows(first_value, header, writer, depth + 2, options)
            else:
                # Fall back to list format for non-uniform arrays of objects
                writer.push(
                    depth, f"{LIST_ITEM_PREFIX}{encoded_key}[{len(first_value)}]:"
                )
                for item in first_value:
                    encode_object_as_list_item(item, writer, depth + 1, options)
        else:
            # Complex arrays on separate lines (array of arrays, etc.)
            writer.push(depth, f"{LIST_ITEM_PREFIX}{encoded_key}[{len(first_value)}]:")

            # Encode array contents at depth + 1
            for item in first_value:
                if is_json_primitive(item):
                    _check_type(
                        item, (str, int, float, bool, type(None)), "JsonPrimitive"
                    )
                    writer.push(
                        depth + 1,
                        f"{LIST_ITEM_PREFIX}{encode_primitive(item, options.delimiter, options.quote)}",
                    )
                elif is_json_array(item) and is_array_of_primitives(item):
                    _check_type(item, list, "JsonArray")
                    inline = format_inline_array(
                        item, options.delimiter, options.quote, None, options.length_marker
                    )
                    writer.push(depth + 1, f"{LIST_ITEM_PREFIX}{inline}")
                elif is_json_object(item):
                    _check_type(item, dict, "JsonObject")
                    encode_object_as_list_item(item, writer, depth + 1, options)
    elif is_json_object(first_value):
        nested_keys = list(first_value.keys())
        if len(nested_keys) == 0:
            writer.push(depth, f"{LIST_ITEM_PREFIX}{encoded_key}:")
        else:
            writer.push(depth, f"{LIST_ITEM_PREFIX}{encoded_key}:")
            encode_object(first_value, writer, depth + 2, options)

    # Remaining keys on indented lines
    for i in range(1, len(keys)):
        key = keys[i]
        key_str = str(key) if not isinstance(key, str) else key
        encode_key_value_pair(key_str, obj[key], writer, depth + 1, options)
