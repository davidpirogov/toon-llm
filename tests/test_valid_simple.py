"""
Comprehensive tests for valid-simple samples.

This module tests all 27 valid-simple samples from the samples/ directory,
covering primitives, strings, objects, and arrays.
"""

import pytest
from pathlib import Path

from pytoon import encode
from tests.samples.sample_data import (
    get_valid_simple_sample,
    get_toon_file_content,
    list_all_valid_simple,
)


# Path to samples directory
SAMPLES_DIR = Path(__file__).parent.parent / "samples"


class TestPrimitives:
    """Test encoding of primitive values."""

    def test_null(self):
        """Test null value encoding."""
        data = get_valid_simple_sample("null")
        expected = get_toon_file_content("valid-simple", "null")
        assert encode(data) == expected
        assert encode(None) == "null"

    def test_bool_true(self):
        """Test boolean true encoding."""
        data = get_valid_simple_sample("bool-true")
        expected = get_toon_file_content("valid-simple", "bool-true")
        assert encode(data) == expected
        assert encode(True) == "true"

    def test_bool_false(self):
        """Test boolean false encoding."""
        data = get_valid_simple_sample("bool-false")
        expected = get_toon_file_content("valid-simple", "bool-false")
        assert encode(data) == expected
        assert encode(False) == "false"

    def test_integer(self):
        """Test positive integer encoding."""
        data = get_valid_simple_sample("integer")
        expected = get_toon_file_content("valid-simple", "integer")
        assert encode(data) == expected
        assert encode(42) == "42"

    def test_negative_integer(self):
        """Test negative integer encoding."""
        data = get_valid_simple_sample("negative-integer")
        expected = get_toon_file_content("valid-simple", "negative-integer")
        assert encode(data) == expected
        assert encode(-7) == "-7"

    def test_float(self):
        """Test float encoding."""
        data = get_valid_simple_sample("float")
        expected = get_toon_file_content("valid-simple", "float")
        assert encode(data) == expected
        assert encode(3.14) == "3.14"


class TestStrings:
    """Test encoding of string values."""

    def test_string_safe(self):
        """Test safe alphanumeric string (no quotes needed)."""
        data = get_valid_simple_sample("string-safe")
        expected = get_toon_file_content("valid-simple", "string-safe")
        assert encode(data) == expected
        assert encode("hello") == "hello"

    def test_string_underscore(self):
        """Test string with underscore (no quotes needed)."""
        data = get_valid_simple_sample("string-underscore")
        expected = get_toon_file_content("valid-simple", "string-underscore")
        assert encode(data) == expected
        assert encode("Ada_99") == "Ada_99"

    def test_string_empty(self):
        """Test empty string (must be quoted)."""
        data = get_valid_simple_sample("string-empty")
        expected = get_toon_file_content("valid-simple", "string-empty")
        assert encode(data) == expected
        assert encode("") == '""'

    def test_string_with_spaces(self):
        """Test string with spaces (internal spaces don't require quoting)."""
        data = get_valid_simple_sample("string-with-spaces")
        expected = get_toon_file_content("valid-simple", "string-with-spaces")
        assert encode(data) == expected
        # Only leading/trailing spaces require quoting
        assert encode("hello world") == "hello world"

    def test_string_ambiguous_true(self):
        """Test string that looks like boolean (must be quoted)."""
        data = get_valid_simple_sample("string-ambiguous-true")
        expected = get_toon_file_content("valid-simple", "string-ambiguous-true")
        assert encode(data) == expected
        assert encode("true") == '"true"'

    def test_string_ambiguous_number(self):
        """Test string that looks like number (must be quoted)."""
        data = get_valid_simple_sample("string-ambiguous-number")
        expected = get_toon_file_content("valid-simple", "string-ambiguous-number")
        assert encode(data) == expected
        assert encode("42") == '"42"'

    def test_string_unicode(self):
        """Test string with unicode characters."""
        data = get_valid_simple_sample("string-unicode")
        expected = get_toon_file_content("valid-simple", "string-unicode")
        assert encode(data) == expected
        assert encode("café") == "café"

    def test_string_emoji(self):
        """Test string with emoji."""
        data = get_valid_simple_sample("string-emoji")
        expected = get_toon_file_content("valid-simple", "string-emoji")
        assert encode(data) == expected
        assert encode("🎉") == "🎉"

    def test_string_control_chars(self):
        """Test string with control characters (must be escaped)."""
        data = get_valid_simple_sample("string-control-chars")
        expected = get_toon_file_content("valid-simple", "string-control-chars")
        assert encode(data) == expected
        # Newline character should be escaped as \n
        assert encode("line1\nline2") == '"line1\\nline2"'

    def test_string_structural(self):
        """Test string with structural characters (must be quoted)."""
        data = get_valid_simple_sample("string-structural")
        expected = get_toon_file_content("valid-simple", "string-structural")
        assert encode(data) == expected
        # Brackets are structural characters
        assert encode("[test]") == '"[test]"'


class TestObjects:
    """Test encoding of objects (dicts)."""

    def test_empty_object(self):
        """Test empty object encoding."""
        data = get_valid_simple_sample("empty-object")
        expected = get_toon_file_content("valid-simple", "empty-object")
        assert encode(data) == expected
        assert encode({}) == ""

    def test_object_basic(self):
        """Test basic object with simple key-value pairs."""
        data = get_valid_simple_sample("object-basic")
        expected = get_toon_file_content("valid-simple", "object-basic")
        assert encode(data) == expected
        result = encode({"name": "Alice", "age": 30})
        assert result == "name: Alice\nage: 30"

    def test_object_with_null(self):
        """Test object with null value."""
        data = get_valid_simple_sample("object-with-null")
        expected = get_toon_file_content("valid-simple", "object-with-null")
        assert encode(data) == expected
        assert encode({"key": None}) == "key: null"

    def test_object_quoted_key(self):
        """Test object with key containing special characters."""
        data = get_valid_simple_sample("object-quoted-key")
        expected = get_toon_file_content("valid-simple", "object-quoted-key")
        assert encode(data) == expected
        # Colon in key requires quoting
        assert encode({"order:id": 7}) == '"order:id": 7'

    def test_object_quoted_value(self):
        """Test object with value containing special characters."""
        data = get_valid_simple_sample("object-quoted-value")
        expected = get_toon_file_content("valid-simple", "object-quoted-value")
        assert encode(data) == expected
        # Comma in value requires quoting
        assert encode({"note": "a,b"}) == 'note: "a,b"'


class TestArrays:
    """Test encoding of arrays (lists)."""

    def test_empty_array(self):
        """Test empty array encoding."""
        data = get_valid_simple_sample("empty-array")
        expected = get_toon_file_content("valid-simple", "empty-array")
        assert encode(data) == expected
        assert encode([]) == "[0]:"

    def test_array_primitives(self):
        """Test array of numbers (inline format)."""
        data = get_valid_simple_sample("array-primitives")
        expected = get_toon_file_content("valid-simple", "array-primitives")
        assert encode(data) == expected
        assert encode([1, 2, 3]) == "[3]: 1,2,3"

    def test_array_strings(self):
        """Test array of strings (inline format)."""
        data = get_valid_simple_sample("array-strings")
        expected = get_toon_file_content("valid-simple", "array-strings")
        assert encode(data) == expected
        assert encode(["a", "b", "c"]) == "[3]: a,b,c"

    def test_array_mixed(self):
        """Test array of mixed primitive types (inline format)."""
        data = get_valid_simple_sample("array-mixed")
        expected = get_toon_file_content("valid-simple", "array-mixed")
        assert encode(data) == expected
        assert encode([1, "two", True, None]) == "[4]: 1,two,true,null"

    def test_array_with_quotes(self):
        """Test array with elements that need quoting."""
        data = get_valid_simple_sample("array-with-quotes")
        expected = get_toon_file_content("valid-simple", "array-with-quotes")
        assert encode(data) == expected
        # Empty string and comma-containing string must be quoted
        assert encode(["", "a,b", "true"]) == '[3]: "","a,b","true"'

    def test_array_tabular(self):
        """Test array of uniform objects (tabular format)."""
        data = get_valid_simple_sample("array-tabular")
        expected = get_toon_file_content("valid-simple", "array-tabular")
        result = encode(data)
        assert result == expected
        # Verify tabular format structure
        assert "[2]{id,name}:" in result
        assert "Alice" in result
        assert "Bob" in result


@pytest.mark.parametrize("sample_name", list_all_valid_simple())
def test_all_valid_simple_samples(sample_name: str):
    """
    Parameterized test for all valid-simple samples.

    This ensures every sample file has a corresponding data structure
    and encodes correctly.
    """
    data = get_valid_simple_sample(sample_name)
    expected = get_toon_file_content("valid-simple", sample_name)
    result = encode(data)
    assert result == expected, f"Mismatch for sample: {sample_name}"
