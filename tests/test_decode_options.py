"""Tests for DecodeOptions and ResolvedDecodeOptions models."""

import pytest
from pydantic import ValidationError

from toon import DecodeOptions, ResolvedDecodeOptions
from toon.constants import Delimiters


class TestDecodeOptions:
    """Test DecodeOptions model."""

    def test_default_values(self):
        """Test that default values are set correctly."""
        options = DecodeOptions()
        assert options.delimiter == ","

    def test_custom_delimiter_comma(self):
        """Test custom delimiter: comma."""
        options = DecodeOptions(delimiter=",")
        assert options.delimiter == ","

    def test_custom_delimiter_tab(self):
        """Test custom delimiter: tab."""
        options = DecodeOptions(delimiter="\t")
        assert options.delimiter == "\t"

    def test_custom_delimiter_pipe(self):
        """Test custom delimiter: pipe."""
        options = DecodeOptions(delimiter="|")
        assert options.delimiter == "|"

    def test_custom_delimiter_from_constants(self):
        """Test delimiter using Delimiters constants."""
        options = DecodeOptions(delimiter=Delimiters.comma)
        assert options.delimiter == ","

        options = DecodeOptions(delimiter=Delimiters.tab)
        assert options.delimiter == "\t"

        options = DecodeOptions(delimiter=Delimiters.pipe)
        assert options.delimiter == "|"

    def test_model_is_frozen(self):
        """Test that DecodeOptions is immutable after creation."""
        options = DecodeOptions()
        with pytest.raises(ValidationError):
            options.delimiter = "|"  # type: ignore[misc]

    def test_extra_fields_forbidden(self):
        """Test that extra fields are rejected."""
        with pytest.raises(ValidationError):
            DecodeOptions(unknown_field="value")  # type: ignore[call-arg]

    def test_model_serialization(self):
        """Test that model can be serialized to dict."""
        options = DecodeOptions(delimiter="|")
        data = options.model_dump()
        assert data == {"delimiter": "|", "quote": '"'}

    def test_model_deserialization(self):
        """Test that model can be created from dict."""
        data = {"delimiter": "|", "quote": '"'}
        options = DecodeOptions(**data)
        assert options.delimiter == "|"
        assert options.quote == '"'


class TestResolvedDecodeOptions:
    """Test ResolvedDecodeOptions model."""

    def test_create_from_options_default(self):
        """Test from_options with default DecodeOptions."""
        options = DecodeOptions()
        resolved = ResolvedDecodeOptions.from_options(options)
        assert resolved.delimiter == ","
        assert resolved.quote == '"'

    def test_create_from_options_custom_delimiter(self):
        """Test from_options with custom delimiter."""
        options = DecodeOptions(delimiter="|")
        resolved = ResolvedDecodeOptions.from_options(options)
        assert resolved.delimiter == "|"
        assert resolved.quote == '"'

    def test_create_from_options_tab_delimiter(self):
        """Test from_options with tab delimiter."""
        options = DecodeOptions(delimiter="\t")
        resolved = ResolvedDecodeOptions.from_options(options)
        assert resolved.delimiter == "\t"
        assert resolved.quote == '"'

    def test_model_is_frozen(self):
        """Test that ResolvedDecodeOptions is immutable after creation."""
        resolved = ResolvedDecodeOptions(delimiter=",", quote='"')
        with pytest.raises(ValidationError):
            resolved.delimiter = "|"  # type: ignore[misc]

    def test_extra_fields_forbidden(self):
        """Test that extra fields are rejected."""
        with pytest.raises(ValidationError):
            ResolvedDecodeOptions(delimiter=",", quote='"', unknown_field="value")  # type: ignore[call-arg]

    def test_direct_instantiation(self):
        """Test that ResolvedDecodeOptions can be created directly."""
        resolved = ResolvedDecodeOptions(delimiter="|", quote='"')
        assert resolved.delimiter == "|"
        assert resolved.quote == '"'

    def test_model_serialization(self):
        """Test that model can be serialized to dict."""
        resolved = ResolvedDecodeOptions(delimiter="|", quote='"')
        data = resolved.model_dump()
        assert data == {"delimiter": "|", "quote": '"'}

    def test_model_deserialization(self):
        """Test that model can be created from dict."""
        data = {"delimiter": "|", "quote": '"'}
        resolved = ResolvedDecodeOptions(**data)
        assert resolved.delimiter == "|"
        assert resolved.quote == '"'


class TestDecodeOptionsIntegration:
    """Test integration between DecodeOptions and ResolvedDecodeOptions."""

    def test_round_trip_conversion(self):
        """Test that options can be converted and back."""
        original = DecodeOptions(delimiter="|")
        resolved = ResolvedDecodeOptions.from_options(original)
        # Create new DecodeOptions with same values
        reconstructed = DecodeOptions(delimiter=resolved.delimiter, quote=resolved.quote)
        assert original.delimiter == reconstructed.delimiter
        assert original.quote == reconstructed.quote

    def test_multiple_conversions_idempotent(self):
        """Test that multiple conversions produce same result."""
        options = DecodeOptions(delimiter="\t")
        resolved1 = ResolvedDecodeOptions.from_options(options)
        resolved2 = ResolvedDecodeOptions.from_options(options)
        assert resolved1.delimiter == resolved2.delimiter
        assert resolved1.quote == resolved2.quote

    def test_all_delimiters_preserve_values(self):
        """Test that all delimiter types preserve values correctly."""
        delimiters = [",", "\t", "|", ";", " "]
        for delimiter in delimiters:
            options = DecodeOptions(delimiter=delimiter)
            resolved = ResolvedDecodeOptions.from_options(options)
            assert resolved.delimiter == delimiter
            assert resolved.quote == '"'
