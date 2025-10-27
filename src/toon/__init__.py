"""
TOON LLM: A human-readable data serialization format for Python.

TOON LLM provides a clean, readable way to serialize Python data structures
into a format that's more compact and easier to read than JSON, while
maintaining full compatibility with JSON-like data structures.

Basic usage:
    >>> from toon import encode, decode
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

from toon.constants import Delimiters
from toon.errors import DecodeError, EncodeError
from toon.types import (
    DecodeOptions,
    EncodeOptions,
    JsonArray,
    JsonObject,
    JsonPrimitive,
    JsonValue,
    ResolvedDecodeOptions,
    ResolvedEncodeOptions,
)
from toon.utils import decode, encode

__version__ = _get_version("toon-llm")

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
