"""
Primitive value encoding and string handling utilities.

This module provides functions for encoding primitive values (strings, numbers,
booleans, null), handling string escaping and quoting, key encoding, and header
formatting for arrays and tables.
"""

import re
from typing import Literal, Optional, Sequence, Union

from pytoon.constants import (
    BACKSLASH,
    COMMA,
    DEFAULT_DELIMITER,
    DOUBLE_QUOTE,
    FALSE_LITERAL,
    LIST_ITEM_MARKER,
    NULL_LITERAL,
    TRUE_LITERAL,
)
from pytoon.types import JsonPrimitive


def encode_primitive(value: JsonPrimitive, delimiter: str = COMMA) -> str:
    """
    Encode a JSON primitive value to a string.

    Args:
        value: The primitive value (str, int, float, bool, or None)
        delimiter: The delimiter being used (affects string quoting)

    Returns:
        The encoded string representation

    Examples:
        >>> encode_primitive(None, ",")
        'null'
        >>> encode_primitive(True, ",")
        'true'
        >>> encode_primitive(42, ",")
        '42'
        >>> encode_primitive("hello", ",")
        'hello'
    """
    if value is None:
        return NULL_LITERAL

    if isinstance(value, bool):
        return TRUE_LITERAL if value else FALSE_LITERAL

    if isinstance(value, (int, float)):
        return str(value)

    # String
    return encode_string_literal(value, delimiter)


def encode_string_literal(value: str, delimiter: str = COMMA) -> str:
    r"""
    Encode a string value, adding quotes and escaping if necessary.

    Strings that are safe to leave unquoted are returned as-is.
    Otherwise, they are escaped and wrapped in double quotes.

    Args:
        value: The string to encode
        delimiter: The delimiter being used (affects safety check)

    Returns:
        The encoded string, quoted if necessary

    Examples:
        >>> encode_string_literal("hello", ",")
        'hello'
        >>> encode_string_literal("hello, world", ",")
        '"hello, world"'
        >>> encode_string_literal("line1\nline2", ",")
        '"line1\\nline2"'
    """
    if is_safe_unquoted(value, delimiter):
        return value

    return f"{DOUBLE_QUOTE}{escape_string(value)}{DOUBLE_QUOTE}"


def escape_string(value: str) -> str:
    r"""
    Escape special characters in a string for quoted output.

    Escapes backslashes, double quotes, newlines, carriage returns, and tabs.

    Args:
        value: The string to escape

    Returns:
        The escaped string

    Examples:
        >>> escape_string('hello "world"')
        'hello \\"world\\"'
        >>> escape_string('line1\nline2')
        'line1\\nline2'
    """
    return (
        value.replace(BACKSLASH, f"{BACKSLASH}{BACKSLASH}")
        .replace(DOUBLE_QUOTE, f"{BACKSLASH}{DOUBLE_QUOTE}")
        .replace("\n", f"{BACKSLASH}n")
        .replace("\r", f"{BACKSLASH}r")
        .replace("\t", f"{BACKSLASH}t")
    )


def is_safe_unquoted(value: str, delimiter: str = COMMA) -> bool:
    """
    Check if a string is safe to leave unquoted.

    A string needs quoting if it:
    - Is empty
    - Has leading/trailing whitespace
    - Matches reserved words (true, false, null)
    - Looks like a number
    - Contains structural characters (:, [, ], {, })
    - Contains the delimiter
    - Contains quotes or backslashes
    - Contains control characters (newline, tab, etc.)
    - Starts with a hyphen (list marker)

    Args:
        value: The string to check
        delimiter: The delimiter being used

    Returns:
        True if the string can be safely left unquoted

    Examples:
        >>> is_safe_unquoted("hello", ",")
        True
        >>> is_safe_unquoted("", ",")
        False
        >>> is_safe_unquoted("true", ",")
        False
        >>> is_safe_unquoted("42", ",")
        False
    """
    # Empty string
    if not value:
        return False

    # Whitespace padding
    if value != value.strip():
        return False

    # Reserved words
    if value in (TRUE_LITERAL, FALSE_LITERAL, NULL_LITERAL):
        return False

    # Numeric-like strings
    if _is_numeric_like(value):
        return False

    # Colon (always structural)
    if ":" in value:
        return False

    # Quotes and backslash (always need escaping)
    if '"' in value or BACKSLASH in value:
        return False

    # Brackets and braces (always structural)
    if re.search(r"[\[\]{}]", value):
        return False

    # Control characters (newline, carriage return, tab)
    if re.search(r"[\n\r\t]", value):
        return False

    # Active delimiter
    if delimiter in value:
        return False

    # Hyphen at start (list marker)
    if value.startswith(LIST_ITEM_MARKER):
        return False

    return True


def _is_numeric_like(value: str) -> bool:
    """
    Check if a string looks like a number.

    Matches integers, floats, scientific notation, and numbers with leading zeros.

    Args:
        value: The string to check

    Returns:
        True if the string looks numeric
    """
    # Match numbers like: 42, -3.14, 1e-6, etc.
    if re.match(r"^-?\d+(?:\.\d+)?(?:e[+-]?\d+)?$", value, re.IGNORECASE):
        return True
    # Match numbers with leading zeros like: 05, 007
    if re.match(r"^0\d+$", value):
        return True
    return False


def encode_key(key: str) -> str:
    """
    Encode an object key, quoting if necessary.

    Keys that consist only of letters, digits, underscores, and dots can be
    left unquoted. All other keys must be quoted and escaped.

    Args:
        key: The key string to encode

    Returns:
        The encoded key, quoted if necessary

    Examples:
        >>> encode_key("name")
        'name'
        >>> encode_key("first_name")
        'first_name'
        >>> encode_key("user.name")
        'user.name'
        >>> encode_key("first name")
        '"first name"'
        >>> encode_key("123")
        '"123"'
    """
    if _is_valid_unquoted_key(key):
        return key

    return f"{DOUBLE_QUOTE}{escape_string(key)}{DOUBLE_QUOTE}"


def _is_valid_unquoted_key(key: str) -> bool:
    """
    Check if a key can be left unquoted.

    Valid unquoted keys start with a letter or underscore and contain only
    letters, digits, underscores, and dots.

    Args:
        key: The key to check

    Returns:
        True if the key can be safely left unquoted
    """
    return bool(re.match(r"^[A-Z_][\w.]*$", key, re.IGNORECASE))


def join_encoded_values(values: Sequence[JsonPrimitive], delimiter: str = COMMA) -> str:
    """
    Encode and join multiple primitive values with a delimiter.

    Args:
        values: Sequence of primitive values to encode
        delimiter: The delimiter to use for joining

    Returns:
        Encoded values joined by the delimiter

    Examples:
        >>> join_encoded_values([1, 2, 3], ",")
        '1,2,3'
        >>> join_encoded_values(["a", "b", "c"], " | ")
        'a | b | c'
        >>> join_encoded_values([True, False, None], ",")
        'true,false,null'
    """
    return delimiter.join(encode_primitive(v, delimiter) for v in values)


def format_header(
    length: int,
    *,
    key: Optional[str] = None,
    fields: Optional[Sequence[str]] = None,
    delimiter: str = COMMA,
    length_marker: Union[Literal["#"], Literal[False]] = False,
) -> str:
    """
    Format a header line for arrays and tables.

    Headers include:
    - Optional key prefix (for object properties that are arrays)
    - Array length with optional # marker
    - Delimiter indicator (if non-default)
    - Optional field names (for tabular format)
    - Trailing colon

    Args:
        length: The length of the array
        key: Optional key name for object properties
        fields: Optional field names for tabular arrays
        delimiter: The delimiter being used
        length_marker: Optional "#" prefix for the length

    Returns:
        Formatted header string

    Examples:
        >>> format_header(3)
        '[3]:'
        >>> format_header(3, length_marker="#")
        '[#3]:'
        >>> format_header(5, key="items")
        'items[5]:'
        >>> format_header(2, fields=["name", "age"], delimiter=",")
        '[2]{name,age}:'
        >>> format_header(2, delimiter="|")
        '[2|]:'
    """
    header = ""

    # Add key prefix if provided
    if key:
        header += encode_key(key)

    # Add length with optional marker and delimiter indicator
    header += "["
    if length_marker:
        header += length_marker
    header += str(length)
    if delimiter != DEFAULT_DELIMITER:
        header += delimiter
    header += "]"

    # Add field names if provided
    if fields:
        encoded_fields = [encode_key(f) for f in fields]
        header += f"{{{delimiter.join(encoded_fields)}}}"

    # Add trailing colon
    header += ":"

    return header
