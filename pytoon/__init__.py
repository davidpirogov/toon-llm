"""
PyToon: A human-readable data serialization format for Python.

PyToon provides a clean, readable way to serialize Python data structures
into a format that's more compact and easier to read than JSON, while
maintaining full compatibility with JSON-like data structures.

Basic usage:
    >>> from pytoon import encode
    >>> data = {"name": "Alice", "age": 30, "active": True}
    >>> print(encode(data))
    name: Alice
    age: 30
    active: true

Features:
    - Automatic type normalization (datetime, dataclass, Pydantic models, etc.)
    - Multiple array formats (inline, tabular, list)
    - Configurable delimiters and indentation
    - Safe string quoting and escaping
    - Preserves key order in objects
"""

from typing import Any, Literal, Union

from pytoon.types import (
    EncodeOptions,
    ResolvedEncodeOptions,
    JsonPrimitive,
    JsonArray,
    JsonObject,
    JsonValue,
)
from pytoon.constants import Delimiters
from pytoon.normalize import normalize_value
from pytoon.encoders import encode_value

__version__ = "0.1.0"

__all__ = [
    "encode",
    "EncodeOptions",
    "Delimiters",
    "JsonPrimitive",
    "JsonArray",
    "JsonObject",
    "JsonValue",
]


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
        indent: Number of spaces per indentation level (default: 2, minimum: 0)
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
