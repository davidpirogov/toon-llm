"""This module contains utility functions for the PyToon library."""

from typing import Any, Literal, Union

from pytoon.decoders import ToonDecoder
from pytoon.encoders import encode_value
from pytoon.normalize import normalize_value
from pytoon.types import DecodeOptions, EncodeOptions, JsonValue, ResolvedDecodeOptions, ResolvedEncodeOptions


def encode(
    data: Any,
    *,
    indent: int = 2,
    delimiter: str = ",",
    length_marker: Union[Literal["#"], Literal[False]] = False,
) -> str:
    r"""
    Encode Python data structures into PyToon format.

    This is the main entry point for the PyToon library. It accepts any Python
    object and converts it to a human-readable text format.

    Type conversions:
        - Primitives (str, int, float, bool, None) pass through
        - datetime objects → ISO 8601 strings
        - dataclasses → dicts
        - Pydantic models → dicts
        - sets → sorted lists
        - lists/tuples → lists
        - Non-serializable values → None

    Args:
        data: Any Python object to encode
        indent: Number of spaces per indentation level (default: 2, minimum: 1)
        delimiter: Delimiter for arrays and tables (default: ",")
                  Common options: "," (comma), "\t" (tab), "|" (pipe)
        length_marker: Optional "#" prefix for array lengths (default: False)
                      When "#", arrays render as [#N] instead of [N]

    Returns:
        PyToon-formatted string

    Raises:
        ValidationError: If options are invalid (e.g., negative indent)

    Examples:
        >>> # Simple object
        >>> encode({"name": "Alice", "age": 30})
        'name: Alice\nage: 30'

        >>> # Nested structure
        >>> encode({"user": {"name": "Bob", "tags": ["admin", "user"]}})
        'user:\n  name: Bob\n  tags[2]: admin,user'

        >>> # Custom indentation and delimiter
        >>> encode([1, 2, 3], indent=4, delimiter="|")
        '[3|]: 1|2|3'

        >>> # With length marker
        >>> encode([1, 2, 3], length_marker="#")
        '[#3]: 1,2,3'

        >>> # Tabular data
        >>> users = [
        ...     {"name": "Alice", "age": 30},
        ...     {"name": "Bob", "age": 25},
        ... ]
        >>> encode(users)
        '[2]{name,age}:\nAlice,30\nBob,25'
    """
    # Create and validate options
    options = EncodeOptions(
        indent=indent,
        delimiter=delimiter,
        length_marker=length_marker,
    )

    # Resolve options (convert indent to string)
    resolved = ResolvedEncodeOptions.from_options(options)

    # Normalize data to JSON-compatible values
    normalized = normalize_value(data)

    # Encode to PyToon format
    return encode_value(normalized, resolved)


def decode(
    text: str,
    *,
    delimiter: str = ",",
) -> JsonValue:
    r"""
    Decode TOON format string to Python data structures.

    This is the main entry point for parsing TOON format strings back into
    Python data structures. It handles all TOON format variants including
    custom delimiters and various array formats.

    Args:
        text: TOON format string to parse
        delimiter: Delimiter character used in the TOON format (default: ",")
                  Common options: "," (comma), "\t" (tab), "|" (pipe)
                  Must match the delimiter used during encoding

    Returns:
        Python data structure (dict, list, or primitive)

    Raises:
        DecodeError: If parsing fails due to malformed TOON format

    Examples:
        >>> # Simple object
        >>> decode("name: Alice\\nage: 30")
        {'name': 'Alice', 'age': 30}

        >>> # Inline array
        >>> decode("[3]: 1,2,3")
        [1, 2, 3]

        >>> # Array with custom delimiter
        >>> decode("[3|]: a|b|c", delimiter="|")
        ['a', 'b', 'c']

        >>> # Tabular data
        >>> decode("[2]{name,age}:\\nAlice,30\\nBob,25")
        [{'name': 'Alice', 'age': 30}, {'name': 'Bob', 'age': 25}]

        >>> # Round-trip encoding/decoding
        >>> data = {"user": {"name": "Bob", "tags": ["admin", "user"]}}
        >>> encoded = encode(data)
        >>> decoded = decode(encoded)
        >>> decoded == data
        True

        >>> # Custom delimiter round-trip
        >>> encoded = encode([1, 2, 3], delimiter="|")
        >>> decode(encoded, delimiter="|")
        [1, 2, 3]
    """
    # Create and validate options
    options = DecodeOptions(delimiter=delimiter)

    # Resolve options
    resolved = ResolvedDecodeOptions.from_options(options)

    # Create decoder with resolved options
    decoder = ToonDecoder(resolved)

    # Decode from PyToon format
    return decoder.decode(text)
