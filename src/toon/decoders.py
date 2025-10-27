"""
TOON format decoder implementation.

This module provides functionality to parse TOON format strings back into
Python data structures, supporting all TOON format variants including
different delimiters, length markers, and array formats.
"""

import re

from toon.errors import DecodeError
from toon.types import (
    JsonArray,
    JsonObject,
    JsonPrimitive,
    JsonValue,
    ResolvedDecodeOptions,
)


class ToonDecoder:
    """
    TOON format decoder.

    Parses TOON format strings into Python data structures, handling all
    format variants including custom delimiters and length markers.
    """

    def __init__(self, options: ResolvedDecodeOptions):
        """
        Initialize decoder with configuration.

        Args:
            options: Resolved decoding options including delimiter
        """
        self.options = options
        self.delimiter_pattern = re.escape(options.delimiter)

    def decode(self, text: str) -> JsonValue:
        """
        Decode TOON format string to Python data structure.

        Args:
            text: TOON format string to parse

        Returns:
            Python data structure (dict, list, or primitive)

        Raises:
            DecodeError: If parsing fails
        """
        if not text.strip():
            return ""

        lines = text.split("\n")
        return self._parse_value(lines, 0, 0)[0]

    def _parse_value(
        self, lines: list[str], line_idx: int, indent: int
    ) -> tuple[JsonValue, int]:
        """Parse a value from the given position in lines."""
        line = lines[line_idx].rstrip()

        # Empty object
        if not line:
            return {}, line_idx + 1

        # Check indentation
        current_indent = len(line) - len(line.lstrip())
        if current_indent != indent:
            raise DecodeError(
                f"Unexpected indentation at line {line_idx + 1}: expected {indent}, got {current_indent}"
            )

        # Array format
        stripped = line.strip()
        if stripped.startswith("["):
            return self._parse_array(lines, line_idx, indent)

        # List item format (- prefix)
        if stripped.startswith("-"):
            return self._parse_list_item(lines, line_idx, indent)

        # Object key-value pair (or key with nested value)
        if ": " in line or stripped.endswith(":"):
            return self._parse_object(lines, line_idx, indent)

        # Primitive value
        return self._parse_primitive(stripped), line_idx + 1

    def _parse_array(
        self, lines: list[str], line_idx: int, indent: int
    ) -> tuple[JsonArray, int]:
        """Parse array format."""
        line = lines[line_idx].strip()

        # Parse array header [length] or [length]:
        header_match = re.match(r"^\[([^\]]+)\](.*)$", line)
        if not header_match:
            raise DecodeError(f"Invalid array header at line {line_idx + 1}: {line}")

        length_part = header_match.group(1)
        remainder = header_match.group(2)

        # Parse length and optional length marker
        length_marker = ""
        if length_part.startswith("#"):
            length_marker = "#"
            length_str = length_part[1:]
        else:
            length_str = length_part

        # Remove delimiter suffix if present (e.g., "3|" -> "3", "3\t" -> "3")
        # The delimiter can be at the end of the length string
        length_str_clean = length_str.rstrip(self.options.delimiter)

        try:
            expected_length = int(length_str_clean)
        except ValueError as e:
            raise DecodeError(
                f"Invalid array length at line {line_idx + 1}: {length_str}"
            ) from e

        # Check for tabular format header: [length]{fields}:
        if remainder.strip().startswith("{"):
            return self._parse_tabular_array(
                lines, line_idx, indent, expected_length, length_marker
            )

        # Check if inline array (remainder contains values)
        if remainder.strip():
            if not remainder.startswith(":"):
                raise DecodeError(
                    f"Expected ':' after array length at line {line_idx + 1}"
                )
            values_text = remainder[1:].strip()
            if values_text:
                # Inline array with values on same line
                values = self._parse_inline_array_values(values_text)
                if len(values) != expected_length:
                    raise DecodeError(
                        f"Array length mismatch at line {line_idx + 1}: expected {expected_length}, got {len(values)}"
                    )
                return values, line_idx + 1
            # If remainder is just ":" with no values, fall through to multi-line parsing

        # Multi-line array - check next line
        next_line_idx = line_idx + 1
        if next_line_idx >= len(lines):
            return [], line_idx + 1

        next_line = lines[next_line_idx].rstrip()
        next_indent = len(next_line) - len(next_line.lstrip()) if next_line else 0

        # Tabular format detection (multi-line tabular without inline header)
        if next_indent > indent and "{" in next_line:
            return self._parse_tabular_array(
                lines, line_idx, indent, expected_length, length_marker
            )

        # List format
        return self._parse_list_array(lines, line_idx, indent, expected_length)

    def _parse_inline_array_values(self, values_text: str) -> JsonArray:
        """Parse inline array values."""
        if not values_text:
            return []

        # Split by delimiter, but be careful about quoted values
        values = []
        current = ""
        in_quotes = False
        i = 0

        while i < len(values_text):
            char = values_text[i]

            if char == '"' and (i == 0 or values_text[i - 1] != "\\"):
                in_quotes = not in_quotes
                current += char
            elif not in_quotes and char == self.options.delimiter:
                values.append(self._parse_primitive(current.strip()))
                current = ""
            else:
                current += char
            i += 1

        if current.strip():
            values.append(self._parse_primitive(current.strip()))

        return values

    def _parse_tabular_array(
        self,
        lines: list[str],
        line_idx: int,
        indent: int,
        expected_length: int,
        length_marker: str,
    ) -> tuple[JsonArray, int]:
        """Parse tabular array format."""
        line = lines[line_idx].strip()
        header_match = re.match(r"^\[([^\]]+)\](.*)$", line)
        if not header_match:
            raise DecodeError(f"Invalid array header at line {line_idx + 1}: {line}")
        remainder = header_match.group(2)

        # Parse header fields - can be inline like "{name,age}:" or on next line
        if remainder.startswith("{"):
            # Inline header: [2]{name,age}:
            if not remainder.endswith(":"):
                raise DecodeError(
                    f"Expected ':' after tabular header at line {line_idx + 1}"
                )
            header_text = remainder[:-1].strip()  # Remove trailing ':'
        elif remainder.startswith(":"):
            # Header on same line after colon: [2]: {name,age}
            header_text = remainder[1:].strip()
        else:
            raise DecodeError(
                f"Expected tabular header after array length at line {line_idx + 1}"
            )

        if not header_text.startswith("{") or not header_text.endswith("}"):
            raise DecodeError(
                f"Invalid tabular header at line {line_idx + 1}: {header_text}"
            )

        fields_text = header_text[1:-1]
        fields = [
            f.strip().strip('"') for f in fields_text.split(self.options.delimiter)
        ]

        # Parse data rows
        rows = []
        current_idx = line_idx + 1

        while current_idx < len(lines):
            current_line = lines[current_idx].rstrip()
            current_indent = len(current_line) - len(current_line.lstrip())

            if not current_line.strip():
                current_idx += 1
                continue

            if current_indent < indent:
                break

            # Parse row values
            row_values = self._parse_inline_array_values(current_line.strip())
            if len(row_values) != len(fields):
                raise DecodeError(
                    f"Row field count mismatch at line {current_idx + 1}: expected {len(fields)}, got {len(row_values)}"
                )

            # Create object from fields and values
            row_obj = {}
            for field, value in zip(fields, row_values, strict=True):
                row_obj[field] = value
            rows.append(row_obj)

            current_idx += 1

        if len(rows) != expected_length:
            raise DecodeError(
                f"Tabular array length mismatch: expected {expected_length}, got {len(rows)}"
            )

        return rows, current_idx

    def _parse_list_array(
        self, lines: list[str], line_idx: int, indent: int, expected_length: int
    ) -> tuple[JsonArray, int]:
        """Parse list format array."""
        items = []
        current_idx = line_idx + 1

        while current_idx < len(lines) and len(items) < expected_length:
            current_line = lines[current_idx].rstrip()
            current_indent = len(current_line) - len(current_line.lstrip())

            if not current_line.strip():
                current_idx += 1
                continue

            if current_indent < indent:
                break

            if current_line.strip().startswith("-"):
                item, next_idx = self._parse_list_item(
                    lines, current_idx, current_indent
                )
                items.append(item)
                current_idx = next_idx
            else:
                # Single value on line
                items.append(self._parse_primitive(current_line.strip()))
                current_idx += 1

        if len(items) != expected_length:
            raise DecodeError(
                f"List array length mismatch: expected {expected_length}, got {len(items)}"
            )

        return items, current_idx

    def _parse_list_item(
        self, lines: list[str], line_idx: int, indent: int
    ) -> tuple[JsonValue, int]:
        """Parse list item format."""
        line = lines[line_idx].strip()
        if not line.startswith("-"):
            raise DecodeError(f"Expected list item at line {line_idx + 1}")

        # First line content after "- "
        first_content = line[1:].strip()

        # Check if it's an array format
        if first_content.startswith("["):
            # Parse as inline array: "- [2]: a,b"
            temp_lines = [first_content]
            array_value, _ = self._parse_array(temp_lines, 0, 0)
            return array_value, line_idx + 1
        elif ": " in first_content:
            # Object format
            return self._parse_object_from_list_item(lines, line_idx, indent)
        else:
            # Simple value
            return self._parse_primitive(first_content), line_idx + 1

    def _parse_object_from_list_item(
        self, lines: list[str], line_idx: int, indent: int
    ) -> tuple[JsonObject, int]:
        """Parse object starting from list item."""
        line = lines[line_idx].strip()
        if not line.startswith("-"):
            raise DecodeError(f"Expected list item at line {line_idx + 1}")

        # Parse first key-value pair
        first_content = line[1:].strip()
        if ": " not in first_content:
            raise DecodeError(
                f"Expected key-value pair in list item at line {line_idx + 1}"
            )

        key_raw, value = first_content.split(": ", 1)
        key = self._parse_key(key_raw)
        obj: JsonObject = {key: self._parse_primitive(value)}

        # Parse additional key-value pairs
        current_idx = line_idx + 1
        while current_idx < len(lines):
            current_line = lines[current_idx].rstrip()
            current_indent = len(current_line) - len(current_line.lstrip())

            if not current_line.strip():
                current_idx += 1
                continue

            if current_indent < indent:
                break

            # Check if it's a new list item (starts with "-") - stop parsing this object
            if current_line.strip().startswith("-"):
                break

            # Check if line has a key (either "key: value" or "key:")
            stripped_line = current_line.strip()
            if ": " in stripped_line or stripped_line.endswith(":"):
                # Parse the key-value pair
                if ": " in stripped_line:
                    key_raw, value = stripped_line.split(": ", 1)
                elif stripped_line.endswith(":"):
                    key_raw = stripped_line[:-1]  # Remove trailing colon
                    value = ""
                else:
                    raise DecodeError(
                        f"Expected key-value pair at line {current_idx + 1}"
                    )

                # Check if key contains array syntax like "data[2]" or "data[2]{fields}"
                array_match = re.match(r"^(\w+)\[([^\]]+)\](.*)$", key_raw)
                if array_match:
                    # This is an array field
                    key = array_match.group(1)
                    length_info = array_match.group(2)
                    remainder = array_match.group(3)  # Could be empty or {fields}

                    # Parse length and optional delimiter/length marker
                    if length_info.startswith("#"):
                        length_str = length_info[1:]
                    else:
                        length_str = length_info

                    # Remove delimiter from length if present
                    if length_str and not length_str[-1].isdigit():
                        length_str = length_str[:-1]

                    try:
                        expected_length = int(length_str)
                    except ValueError as e:
                        raise DecodeError(
                            f"Invalid array length at line {current_idx + 1}: {length_str}"
                        ) from e

                    # Check if it's tabular format: has {fields} in remainder
                    if remainder.startswith("{"):
                        # Tabular format - extract fields part
                        # remainder format: {fields}
                        brace_end = remainder.find("}")
                        if brace_end == -1:
                            raise DecodeError(
                                f"Invalid tabular array header at line {current_idx + 1}"
                            )

                        fields_text = remainder[1:brace_end]
                        fields = [
                            f.strip().strip('"')
                            for f in fields_text.split(self.options.delimiter)
                        ]  # Parse data rows
                        rows = []
                        row_idx = current_idx + 1
                        while row_idx < len(lines):
                            row_line = lines[row_idx].rstrip()
                            row_indent = len(row_line) - len(row_line.lstrip())

                            if not row_line.strip():
                                row_idx += 1
                                continue

                            if row_indent <= current_indent:
                                break

                            # Parse row values
                            row_values = self._parse_inline_array_values(
                                row_line.strip()
                            )
                            if len(row_values) != len(fields):
                                raise DecodeError(
                                    f"Row field count mismatch at line {row_idx + 1}: expected {len(fields)}, got {len(row_values)}"
                                )

                            # Create object from fields and values
                            row_obj = {}
                            for field, value in zip(fields, row_values, strict=True):
                                row_obj[field] = value
                            rows.append(row_obj)
                            row_idx += 1

                        if len(rows) != expected_length:
                            raise DecodeError(
                                f"Tabular array length mismatch at line {current_idx + 1}: expected {expected_length}, got {len(rows)}"
                            )

                        obj[key] = rows
                        current_idx = row_idx
                    elif value:
                        # Inline array values
                        array_values = self._parse_inline_array_values(value)
                        if len(array_values) != expected_length:
                            raise DecodeError(
                                f"Array length mismatch at line {current_idx + 1}: expected {expected_length}, got {len(array_values)}"
                            )
                        obj[key] = array_values
                        current_idx += 1
                    else:
                        # Multi-line array - will be filled by next iteration
                        obj[key] = ""
                        current_idx += 1
                else:
                    # Regular key-value pair
                    key = self._parse_key(key_raw)
                    if value:
                        obj[key] = self._parse_primitive(value)
                    else:
                        # Nested object - will be filled by next iteration
                        obj[key] = ""
                    current_idx += 1
            elif current_indent > indent:
                # Nested structure - parse it and assign to the last key
                nested_value, next_idx = self._parse_value(
                    lines, current_idx, current_indent
                )
                if obj:
                    last_key = list(obj.keys())[-1]
                    obj[last_key] = nested_value
                current_idx = next_idx
            else:
                # Shouldn't happen - break to be safe
                break

        return obj, current_idx

    def _parse_object(
        self, lines: list[str], line_idx: int, indent: int
    ) -> tuple[JsonObject, int]:
        """Parse object key-value pairs."""
        line = lines[line_idx].strip()

        # Handle both "key: value" and "key:" (nested object) formats
        if ": " in line:
            key_part, value = line.split(": ", 1)
        elif line.endswith(":"):
            key_part = line[:-1]  # Remove trailing colon
            value = ""
        else:
            raise DecodeError(f"Expected key-value pair at line {line_idx + 1}")

        # Check if key contains array syntax like "tags[2]" or "tags[2]{fields}"
        # Note: quoted keys won't match this pattern, which is correct
        array_match = re.match(r"^(\w+)\[([^\]]+)\](.*)$", key_part)
        if array_match:
            # This is an array field: extract key and parse the array inline
            key = array_match.group(1)
            length_info = array_match.group(2)
            remainder = array_match.group(3)  # Could be empty or {fields}

            # Parse length based on possible length marker
            if length_info.startswith("#"):
                length_str = length_info[1:]
            else:
                length_str = length_info

            # Remove delimiter from length if present (e.g., "3|" -> "3")
            if not length_str[-1].isdigit():
                length_str = length_str[:-1]

            try:
                expected_length = int(length_str)
            except ValueError as e:
                raise DecodeError(
                    f"Invalid array length at line {line_idx + 1}: {length_str}"
                ) from e

            # Check if it's tabular format: has {fields} in remainder
            if remainder.startswith("{"):
                # Tabular format - extract fields part
                brace_end = remainder.find("}")
                if brace_end == -1:
                    raise DecodeError(
                        f"Invalid tabular array header at line {line_idx + 1}"
                    )

                fields_text = remainder[1:brace_end]
                fields = [
                    f.strip().strip('"')
                    for f in fields_text.split(self.options.delimiter)
                ]

                # Parse data rows
                rows = []
                row_idx = line_idx + 1
                while row_idx < len(lines):
                    row_line = lines[row_idx].rstrip()
                    row_indent = len(row_line) - len(row_line.lstrip())

                    if not row_line.strip():
                        row_idx += 1
                        continue

                    if row_indent <= indent:
                        break

                    # Parse row values
                    row_values = self._parse_inline_array_values(row_line.strip())
                    if len(row_values) != len(fields):
                        raise DecodeError(
                            f"Row field count mismatch at line {row_idx + 1}: expected {len(fields)}, got {len(row_values)}"
                        )

                    # Create object from fields and values
                    row_obj = {}
                    for field, value in zip(fields, row_values, strict=True):
                        row_obj[field] = value
                    rows.append(row_obj)
                    row_idx += 1

                if len(rows) != expected_length:
                    raise DecodeError(
                        f"Tabular array length mismatch at line {line_idx + 1}: expected {expected_length}, got {len(rows)}"
                    )

                obj: JsonObject = {key: rows}
                current_idx = row_idx
            # Check if this is a list format array (value is empty and next line has content)
            elif not value.strip() and line_idx + 1 < len(lines):
                next_line = lines[line_idx + 1].rstrip()
                next_indent = (
                    len(next_line) - len(next_line.lstrip()) if next_line else 0
                )

                # If next line is indented more and starts with "-", it's a list format array
                if next_indent > indent and next_line.strip().startswith("-"):
                    # Parse as list format array
                    items, next_idx = self._parse_list_array(
                        lines, line_idx, indent, expected_length
                    )
                    obj: JsonObject = {key: items}
                    # Continue from where list parsing left off to parse additional fields
                    current_idx = next_idx
                else:
                    # Inline format with empty value
                    array_values = self._parse_inline_array_values(value)
                    if len(array_values) != expected_length:
                        raise DecodeError(
                            f"Array length mismatch at line {line_idx + 1}: expected {expected_length}, got {len(array_values)}"
                        )
                    obj: JsonObject = {key: array_values}
                    current_idx = line_idx + 1
            else:
                # Parse inline array values
                array_values = self._parse_inline_array_values(value)
                if len(array_values) != expected_length:
                    raise DecodeError(
                        f"Array length mismatch at line {line_idx + 1}: expected {expected_length}, got {len(array_values)}"
                    )
                obj: JsonObject = {key: array_values}
                current_idx = line_idx + 1
        else:
            # Regular key-value pair - handle quoted keys
            key = self._parse_key(key_part)
            obj = {key: self._parse_primitive(value)}
            current_idx = line_idx + 1

        # Parse additional key-value pairs
        while current_idx < len(lines):
            current_line = lines[current_idx].rstrip()
            current_indent = len(current_line) - len(current_line.lstrip())

            if not current_line.strip():
                current_idx += 1
                continue

            if current_indent < indent:
                break

            # If same indentation level and has key-value pair, it's a peer
            if current_indent == indent and (
                ": " in current_line or current_line.strip().endswith(":")
            ):
                stripped_line = current_line.strip()

                # Handle both "key: value" and "key:" (nested object) formats
                if ": " in stripped_line:
                    key_raw, value = stripped_line.split(": ", 1)
                elif stripped_line.endswith(":"):
                    key_raw = stripped_line[:-1]  # Remove trailing colon
                    value = ""
                else:
                    raise DecodeError(
                        f"Expected key-value pair at line {current_idx + 1}"
                    )

                # Check if key contains array syntax like "tags[2]" or "tags[2]{fields}"
                array_match = re.match(r"^(\w+)\[([^\]]+)\](.*)$", key_raw)
                if array_match:
                    # This is an array field: extract key and parse the array inline
                    key = array_match.group(1)
                    length_info = array_match.group(2)
                    remainder = array_match.group(3)  # Could be empty or {fields}

                    # Parse length and optional delimiter/length marker
                    if length_info.startswith("#"):
                        length_str = length_info[1:]
                    else:
                        length_str = length_info

                    # Remove delimiter from length if present (e.g., "3|" -> "3")
                    if length_str and not length_str[-1].isdigit():
                        length_str = length_str[:-1]

                    try:
                        expected_length = int(length_str)
                    except ValueError as e:
                        raise DecodeError(
                            f"Invalid array length at line {current_idx + 1}: {length_str}"
                        ) from e

                    # Check if it's tabular format: has {fields} in remainder
                    if remainder.startswith("{"):
                        # Tabular format - extract fields part
                        brace_end = remainder.find("}")
                        if brace_end == -1:
                            raise DecodeError(
                                f"Invalid tabular array header at line {current_idx + 1}"
                            )

                        fields_text = remainder[1:brace_end]
                        fields = [
                            f.strip().strip('"')
                            for f in fields_text.split(self.options.delimiter)
                        ]

                        # Parse data rows
                        rows = []
                        row_idx = current_idx + 1
                        while row_idx < len(lines):
                            row_line = lines[row_idx].rstrip()
                            row_indent = len(row_line) - len(row_line.lstrip())

                            if not row_line.strip():
                                row_idx += 1
                                continue

                            if row_indent <= current_indent:
                                break

                            # Parse row values
                            row_values = self._parse_inline_array_values(
                                row_line.strip()
                            )
                            if len(row_values) != len(fields):
                                raise DecodeError(
                                    f"Row field count mismatch at line {row_idx + 1}: expected {len(fields)}, got {len(row_values)}"
                                )

                            # Create object from fields and values
                            row_obj = {}
                            for field, value in zip(fields, row_values, strict=True):
                                row_obj[field] = value
                            rows.append(row_obj)
                            row_idx += 1

                        if len(rows) != expected_length:
                            raise DecodeError(
                                f"Tabular array length mismatch at line {current_idx + 1}: expected {expected_length}, got {len(rows)}"
                            )

                        obj[key] = rows
                        current_idx = row_idx
                        continue
                    # Check if this is a list format array (value is empty and next line has content)
                    elif not value.strip() and current_idx + 1 < len(lines):
                        next_line = lines[current_idx + 1].rstrip()
                        next_indent = (
                            len(next_line) - len(next_line.lstrip()) if next_line else 0
                        )

                        # If next line is indented more and starts with "-", it's a list format array
                        if (
                            next_indent > current_indent
                            and next_line.strip().startswith("-")
                        ):
                            # Parse as list format array
                            items, next_idx = self._parse_list_array(
                                lines, current_idx, current_indent, expected_length
                            )
                            obj[key] = items
                            current_idx = next_idx
                            continue
                        else:
                            # Inline format with empty value
                            array_values = self._parse_inline_array_values(value)
                            if len(array_values) != expected_length:
                                raise DecodeError(
                                    f"Array length mismatch at line {current_idx + 1}: expected {expected_length}, got {len(array_values)}"
                                )
                            obj[key] = array_values
                    else:
                        # Parse inline array values
                        array_values = self._parse_inline_array_values(value)
                        if len(array_values) != expected_length:
                            raise DecodeError(
                                f"Array length mismatch at line {current_idx + 1}: expected {expected_length}, got {len(array_values)}"
                            )
                        obj[key] = array_values
                else:
                    # Regular key-value pair - handle quoted keys
                    key = self._parse_key(key_raw)
                    if value:
                        # Inline value
                        obj[key] = self._parse_primitive(value)
                    else:
                        # Nested object - will be filled by next iteration
                        obj[key] = ""
                current_idx += 1
            elif current_indent > indent:
                # Nested structure - parse it and assign to the last key
                nested_value, next_idx = self._parse_value(
                    lines, current_idx, current_indent
                )
                if obj:
                    last_key = list(obj.keys())[-1]
                    obj[last_key] = nested_value
                current_idx = next_idx
            else:
                # This shouldn't happen but break to be safe
                break

        return obj, current_idx

    def _parse_key(self, key: str) -> str:
        """
        Parse and unescape object key.

        Handles quoted keys by removing quotes and unescaping.

        Args:
            key: Raw key string which may be quoted

        Returns:
            Unquoted and unescaped key string
        """
        if not key:
            return ""

        # Handle quoted keys
        if key.startswith('"') and key.endswith('"'):
            # Remove quotes and unescape
            inner = key[1:-1]
            # Basic unescaping - handle \\ and \"
            inner = inner.replace("\\\\", "\\").replace('\\"', '"')
            return inner

        # Return unquoted key as-is
        return key

    def _parse_primitive(self, value: str) -> JsonPrimitive:
        """Parse primitive value."""
        if not value:
            return ""

        # Handle quoted strings
        if value.startswith('"') and value.endswith('"'):
            # Remove quotes and unescape
            inner = value[1:-1]
            # Basic unescaping - handle \\ and \"
            inner = inner.replace("\\\\", "\\").replace('\\"', '"')
            return inner

        # Handle literals
        if value == "null":
            return None
        elif value == "true":
            return True
        elif value == "false":
            return False

        # Try to parse as number
        try:
            # Integer
            if "." not in value and "e" not in value.lower():
                return int(value)
            else:
                return float(value)
        except ValueError:
            pass

        # Return as string
        return value
