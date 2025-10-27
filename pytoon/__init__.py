"""
PyToon: A human-readable data serialization format for Python.

PyToon provides a clean, readable way to serialize Python data structures
into a format that's more compact and easier to read than JSON, while
maintaining full compatibility with JSON-like data structures.

Basic usage:
    >>> from pytoon import encode, decode
    >>> data = {"name": "Alice", "age": 30, "active": True}
    >>> encoded = encode(data)
    >>> print(encoded)
    name: Alice
    age: 30
    active: true
    >>> decoded = decode(encoded)
    >>> print(decoded)
    {'name': 'Alice', 'age': 30, 'active': True}

Features:
    - Automatic type normalization (datetime, dataclass, Pydantic models, etc.)
    - Multiple array formats (inline, tabular, list)
    - Configurable delimiters and indentation
    - Safe string quoting and escaping
    - Preserves key order in objects
    - Round-trip encoding and decoding
"""

from importlib.metadata import version as _get_version

from pytoon.constants import Delimiters
from pytoon.errors import DecodeError, EncodeError
from pytoon.types import (
    DecodeOptions,
    EncodeOptions,
    JsonArray,
    JsonObject,
    JsonPrimitive,
    JsonValue,
    ResolvedDecodeOptions,
    ResolvedEncodeOptions,
)
from pytoon.utils import decode, encode

__version__ = _get_version("py-toon")

__all__ = [
    "encode",
    "decode",
    "EncodeOptions",
    "ResolvedEncodeOptions",
    "DecodeOptions",
    "ResolvedDecodeOptions",
    "EncodeError",
    "DecodeError",
    "Delimiters",
    "JsonPrimitive",
    "JsonArray",
    "JsonObject",
    "JsonValue",
]
