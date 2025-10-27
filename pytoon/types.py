"""
Type definitions and data models for PyToon encoding.

This module provides type aliases for JSON-like data structures and Pydantic models
for configuration options with validation.
"""

from typing import Literal, Union

from pydantic import BaseModel, ConfigDict, Field

from pytoon.constants import Delimiters

JsonPrimitive = Union[str, int, float, bool, None]
"""A JSON primitive value: string, number, boolean, or null."""

JsonObject = dict[str, "JsonValue"]
"""A JSON object represented as a dictionary with string keys."""

JsonArray = list["JsonValue"]
"""A JSON array represented as a list."""

JsonValue = Union[JsonPrimitive, JsonObject, JsonArray]
"""Any JSON value: primitive, object, or array."""

Depth = int
"""Indentation depth level (non-negative integer)."""


class EncodeOptions(BaseModel):
    """
    Configuration options for PyToon encoding.

    All fields are optional and have sensible defaults. The model is frozen
    after creation to prevent accidental modifications.

    Attributes:
        indent: Number of spaces per indentation level (default: 2, minimum: 1)
        delimiter: Delimiter character for arrays and tables (default: comma)
        length_marker: Optional "#" prefix for array lengths, or False to disable (default: False)

    Examples:
        >>> options = EncodeOptions()  # Use all defaults
        >>> options = EncodeOptions(indent=4, delimiter=Delimiters.pipe)
        >>> options = EncodeOptions(length_marker="#")
    """

    indent: int = Field(
        default=2,
        ge=1,
        description="Number of spaces per indentation level",
    )
    delimiter: str = Field(
        default=Delimiters.comma,
        description="Delimiter for arrays and tables",
    )
    length_marker: Union[Literal["#"], Literal[False]] = Field(
        default=False,
        description="Array length marker prefix",
    )

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        validate_default=True,
    )


class ResolvedEncodeOptions(BaseModel):
    """
    Resolved encoding options with all fields required.

    This is the internal representation used during encoding, where all
    optional values have been resolved to their concrete values.

    Unlike EncodeOptions, this model stores the indent as a string (spaces)
    for efficiency during encoding.

    Attributes:
        indent: Indentation string (spaces repeated)
        delimiter: Delimiter character
        length_marker: Length marker character or False
    """

    indent: str = Field(description="Indentation string (spaces)")
    delimiter: str = Field(description="Delimiter character")
    length_marker: Union[Literal["#"], Literal[False]] = Field(
        description="Length marker prefix or False"
    )

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

    @classmethod
    def from_options(cls, options: EncodeOptions) -> "ResolvedEncodeOptions":
        """
        Create a ResolvedEncodeOptions from an EncodeOptions instance.

        Args:
            options: The source encoding options

        Returns:
            A resolved options instance with indent converted to a string
        """
        return cls(
            indent=" " * options.indent,
            delimiter=options.delimiter,
            length_marker=options.length_marker,
        )


class DecodeOptions(BaseModel):
    r"""
    Configuration options for PyToon decoding.

    All fields are optional and have sensible defaults. The model is frozen
    after creation to prevent accidental modifications.

    Attributes:
        delimiter: Delimiter character used in the TOON format (default: comma)

    Examples:
        >>> options = DecodeOptions()  # Use default
        >>> options = DecodeOptions(delimiter=Delimiters.pipe)
        >>> options = DecodeOptions(delimiter="\t")
    """

    delimiter: str = Field(
        default=Delimiters.comma,
        description="Delimiter for arrays and tables",
    )

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        validate_default=True,
    )


class ResolvedDecodeOptions(BaseModel):
    """
    Resolved decoding options with all fields required.

    This is the internal representation used during decoding, where all
    optional values have been resolved to their concrete values.

    Attributes:
        delimiter: Delimiter character
    """

    delimiter: str = Field(description="Delimiter character")

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

    @classmethod
    def from_options(cls, options: DecodeOptions) -> "ResolvedDecodeOptions":
        """
        Create a ResolvedDecodeOptions from a DecodeOptions instance.

        Args:
            options: The source decoding options

        Returns:
            A resolved options instance
        """
        return cls(delimiter=options.delimiter)
