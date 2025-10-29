"""
Comprehensive tests for valid-simple samples.

This module tests all 27 valid-simple samples from the specification/samples/ directory,
covering primitives, strings, objects, and arrays.

Tests follow the coding standards defined in docs/CODING_STANDARDS.md:
- Uses type hints throughout
- Comprehensive docstrings with examples
- Single responsibility functions
- Clear, descriptive test names
- Organized test classes by functionality
"""

import json

import pytest

from toon import encode
from tests.sample_data import get_sample



class TestPrimitives:
    """Test encoding of primitive values."""

    def test_null(self) -> None:
        """Test null value encoding."""
        expected = get_sample("valid-simple-null")
        assert encode(None) == expected
        assert encode(None) == "null"

    def test_bool_true(self) -> None:
        """Test boolean true encoding."""
        expected = get_sample("valid-simple-bool-true")
        assert encode(True) == expected
        assert encode(True) == "true"

    def test_bool_false(self) -> None:
        """Test boolean false encoding."""
        expected = get_sample("valid-simple-bool-false")
        assert encode(False) == expected
        assert encode(False) == "false"

    def test_integer(self) -> None:
        """Test positive integer encoding."""
        expected = get_sample("valid-simple-integer")
        assert encode(42) == expected
        assert encode(42) == "42"

    def test_negative_integer(self) -> None:
        """Test negative integer encoding."""
        expected = get_sample("valid-simple-negative-integer")
        assert encode(-7) == expected
        assert encode(-7) == "-7"

    def test_float(self) -> None:
        """Test float encoding."""
        expected = get_sample("valid-simple-float")
        assert encode(3.14) == expected
        assert encode(3.14) == "3.14"


class TestFloatJsonCompatibility:
    """Test that float encoding matches json.dumps() behavior.

    This addresses issue #6: Ensure encoder uses JSON defaults for serializing numbers.
    Reference: https://github.com/davidpirogov/toon-llm/issues/6
    """

    def test_float_from_issue_4(self) -> None:
        """Test the specific float from issue #4 (677.822)."""
        test_value = 677.822
        json_output = json.dumps(test_value)
        toon_output = encode(test_value)

        # Should match JSON output exactly
        assert toon_output == json_output
        assert toon_output == "677.822"

    def test_float_precision_cases(self) -> None:
        """Test various floats that previously showed excessive precision."""
        test_cases = [
            677.822,
            123.456789,
            0.1,
            0.12345,
            3.14,
            1.5,
        ]

        for test_value in test_cases:
            json_output = json.dumps(test_value)
            toon_output = encode(test_value)
            assert toon_output == json_output, (
                f"Float {test_value} encoding mismatch: "
                f"JSON={json_output!r}, TOON={toon_output!r}"
            )

    def test_float_whole_numbers_as_integers(self) -> None:
        """Test that whole number floats are encoded as integers (design choice)."""
        # This is intentional for compactness, even though JSON would keep .0
        assert encode(2.0) == "2"
        assert encode(10.0) == "10"
        assert encode(100.0) == "100"
        assert encode(-5.0) == "-5"

    def test_float_scientific_notation(self) -> None:
        """Test that very small/large floats use scientific notation like JSON."""
        # Test values that use scientific notation (non-whole numbers)
        test_cases = [
            1e-10,
            1e-15,
        ]

        for test_value in test_cases:
            json_output = json.dumps(test_value)
            toon_output = encode(test_value)
            assert toon_output == json_output, (
                f"Scientific notation mismatch for {test_value}: "
                f"JSON={json_output!r}, TOON={toon_output!r}"
            )

        # Large whole number floats become integers (design choice for compactness)
        # e.g., 1e10 = 10000000000.0 -> "10000000000" (not "10000000000.0")
        assert encode(1e10) == "10000000000"  # 1e10 is a whole number
        assert encode(1e15) == "1000000000000000"  # 1e15 is a whole number

    def test_float_special_values(self) -> None:
        """Test that special float values (inf, -inf, nan) encode as null."""
        # These are not valid JSON, so we encode as null
        assert encode(float('inf')) == "null"
        assert encode(float('-inf')) == "null"
        assert encode(float('nan')) == "null"


    def test_float_edge_case_arithmetic(self) -> None:
        """Test classic floating point arithmetic edge cases."""
        # Classic case: 0.1 + 0.2
        result = 0.1 + 0.2
        json_output = json.dumps(result)
        toon_output = encode(result)
        assert toon_output == json_output

    def test_object_with_floats(self) -> None:
        """Test encoding objects containing floats matches JSON for the float values."""
        sample = {"ma": {"5": 677.822}}

        # The full object won't match due to TOON's format, but the float should match
        toon_output = encode(sample)

        # Verify the float is encoded correctly within the object
        assert "677.822" in toon_output
        # Should NOT have excessive precision
        assert "677.822000000000003" not in toon_output



class TestStrings:
    """Test encoding of string values."""

    def test_string_safe(self) -> None:
        """Test safe alphanumeric string (no quotes needed)."""
        expected = get_sample("valid-simple-string-safe")
        assert encode("hello") == expected
        assert encode("hello") == "hello"

    def test_string_underscore(self) -> None:
        """Test string with underscore (no quotes needed)."""
        expected = get_sample("valid-simple-string-underscore")
        assert encode("Ada_99") == expected
        assert encode("Ada_99") == "Ada_99"

    def test_string_empty(self) -> None:
        """Test empty string (must be quoted)."""
        expected = get_sample("valid-simple-string-empty")
        assert encode("") == expected
        assert encode("") == '""'

    def test_string_with_spaces(self) -> None:
        """Test string with spaces (internal spaces don't require quoting)."""
        expected = get_sample("valid-simple-string-with-spaces")
        assert encode("hello world") == expected
        # Only leading/trailing spaces require quoting
        assert encode("hello world") == "hello world"

    def test_string_ambiguous_true(self) -> None:
        """Test string that looks like boolean (must be quoted)."""
        expected = get_sample("valid-simple-string-ambiguous-true")
        assert encode("true") == expected
        assert encode("true") == '"true"'

    def test_string_ambiguous_number(self) -> None:
        """Test string that looks like number (must be quoted)."""
        expected = get_sample("valid-simple-string-ambiguous-number")
        assert encode("42") == expected
        assert encode("42") == '"42"'

    def test_string_unicode(self) -> None:
        """Test string with unicode characters."""
        expected = get_sample("valid-simple-string-unicode")
        assert encode("café") == expected
        assert encode("café") == "café"

    def test_string_emoji(self) -> None:
        """Test string with emoji."""
        expected = get_sample("valid-simple-string-emoji")
        assert encode("🚀") == expected
        assert encode("🚀") == "🚀"

    def test_string_control_chars(self) -> None:
        """Test string with control characters (must be escaped)."""
        expected = get_sample("valid-simple-string-control-chars")
        assert encode("line1\nline2") == expected
        # Newline character should be escaped as \n
        assert encode("line1\nline2") == '"line1\\nline2"'

    def test_string_structural(self) -> None:
        """Test string with structural characters (must be quoted)."""
        expected = get_sample("valid-simple-string-structural")
        assert encode("[test]") == expected
        # Brackets are structural characters
        assert encode("[test]") == '"[test]"'


class TestObjects:
    """Test encoding of objects (dicts)."""

    def test_empty_object(self) -> None:
        """Test empty object encoding."""
        expected = get_sample("valid-simple-empty-object")
        assert encode({}) == expected
        assert encode({}) == ""

    def test_object_basic(self) -> None:
        """Test basic object with simple key-value pairs."""
        expected = get_sample("valid-simple-object-basic")
        result = encode({"name": "Alice", "age": 30})
        assert result == expected
        assert result == "name: Alice\nage: 30"

    def test_object_with_null(self) -> None:
        """Test object with null value."""
        expected = get_sample("valid-simple-object-with-null")
        assert encode({"id": 123, "value": None}) == expected
        assert encode({"value": None}) == "value: null"

    def test_object_quoted_key(self) -> None:
        """Test object with key containing special characters."""
        expected = get_sample("valid-simple-object-quoted-key")
        assert encode({"order:id": 7}) == expected
        # Colon in key requires quoting
        assert encode({"order:id": 7}) == '"order:id": 7'

    def test_object_quoted_value(self) -> None:
        """Test object with value containing special characters."""
        expected = get_sample("valid-simple-object-quoted-value")
        assert encode({"note": "a,b"}) == expected
        # Comma in value requires quoting
        assert encode({"note": "a,b"}) == 'note: "a,b"'


class TestArrays:
    """Test encoding of arrays (lists)."""

    def test_empty_array(self) -> None:
        """Test empty array encoding."""
        expected = get_sample("valid-simple-empty-array")
        assert encode([]) == expected
        assert encode([]) == "[0]:"

    def test_array_primitives(self) -> None:
        """Test array of numbers (inline format)."""
        expected = get_sample("valid-simple-array-primitives")
        assert encode([1, 2, 3]) == expected
        assert encode([1, 2, 3]) == "[3]: 1,2,3"

    def test_array_strings(self) -> None:
        """Test array of strings (inline format)."""
        expected = get_sample("valid-simple-array-strings")
        assert encode(["a", "b", "c"]) == expected
        assert encode(["a", "b", "c"]) == "[3]: a,b,c"

    def test_array_mixed(self) -> None:
        """Test array of mixed primitive types (inline format)."""
        expected = get_sample("valid-simple-array-mixed")
        assert encode([1, "two", True, None]) == expected
        assert encode([1, "two", True, None]) == "[4]: 1,two,true,null"

    def test_array_with_quotes(self) -> None:
        """Test array with elements that need quoting."""
        expected = get_sample("valid-simple-array-with-quotes")
        assert encode(["a", "b,c", "d:e"]) == expected
        # Empty string and comma-containing string must be quoted
        assert encode(["", "a,b", "true"]) == '[3]: "","a,b","true"'

    def test_array_tabular(self) -> None:
        """Test array of uniform objects (tabular format)."""
        expected = get_sample("valid-simple-array-tabular")
        result = encode([{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}])
        assert result == expected
        # Verify tabular format structure
        assert "[2]{id,name}:" in result
        assert "Alice" in result
        assert "Bob" in result


# Parameterized tests for comprehensive coverage
VALID_SIMPLE_SAMPLES = [
    "valid-simple-null",
    "valid-simple-bool-true",
    "valid-simple-bool-false",
    "valid-simple-integer",
    "valid-simple-negative-integer",
    "valid-simple-float",
    "valid-simple-string-safe",
    "valid-simple-string-underscore",
    "valid-simple-string-empty",
    "valid-simple-string-with-spaces",
    "valid-simple-string-ambiguous-true",
    "valid-simple-string-ambiguous-number",
    "valid-simple-string-unicode",
    "valid-simple-string-emoji",
    "valid-simple-string-control-chars",
    "valid-simple-string-structural",
    "valid-simple-empty-object",
    "valid-simple-object-basic",
    "valid-simple-object-with-null",
    "valid-simple-object-quoted-key",
    "valid-simple-object-quoted-value",
    "valid-simple-empty-array",
    "valid-simple-array-primitives",
    "valid-simple-array-strings",
    "valid-simple-array-mixed",
    "valid-simple-array-with-quotes",
    "valid-simple-array-tabular",
]


@pytest.mark.parametrize("sample_name", VALID_SIMPLE_SAMPLES)
def test_all_valid_simple_samples(sample_name: str) -> None:
    """
    Parameterized test for all valid simple samples.

    This ensures every valid simple sample file can be loaded and tested.
    Each test verifies that the encoding produces the expected output.

    Args:
        sample_name: Name of the sample file to test
    """
    expected = get_sample(sample_name)

    # For now, we'll test a few key samples directly
    # TODO: Add comprehensive data structure mapping for all samples
    if sample_name == "valid-simple-null":
        assert encode(None) == expected
    elif sample_name == "valid-simple-bool-true":
        assert encode(True) == expected
    elif sample_name == "valid-simple-bool-false":
        assert encode(False) == expected
    elif sample_name == "valid-simple-integer":
        assert encode(42) == expected
    elif sample_name == "valid-simple-negative-integer":
        assert encode(-7) == expected
    elif sample_name == "valid-simple-float":
        assert encode(3.14) == expected
    elif sample_name == "valid-simple-string-safe":
        assert encode("hello") == expected
    elif sample_name == "valid-simple-string-underscore":
        assert encode("Ada_99") == expected
    elif sample_name == "valid-simple-string-empty":
        assert encode("") == expected
    elif sample_name == "valid-simple-string-with-spaces":
        assert encode("hello world") == expected
    elif sample_name == "valid-simple-string-ambiguous-true":
        assert encode("true") == expected
    elif sample_name == "valid-simple-string-ambiguous-number":
        assert encode("42") == expected
    elif sample_name == "valid-simple-string-unicode":
        assert encode("café") == expected
    elif sample_name == "valid-simple-string-emoji":
        assert encode("🚀") == expected
    elif sample_name == "valid-simple-string-control-chars":
        assert encode("line1\nline2") == expected
    elif sample_name == "valid-simple-string-structural":
        assert encode("[test]") == expected
    elif sample_name == "valid-simple-empty-object":
        assert encode({}) == expected
    elif sample_name == "valid-simple-object-basic":
        assert encode({"name": "Alice", "age": 30}) == expected
    elif sample_name == "valid-simple-object-with-null":
        assert encode({"id": 123, "value": None}) == expected
    elif sample_name == "valid-simple-object-quoted-key":
        assert encode({"order:id": 7}) == expected
    elif sample_name == "valid-simple-object-quoted-value":
        assert encode({"note": "a,b"}) == expected
    elif sample_name == "valid-simple-empty-array":
        assert encode([]) == expected
    elif sample_name == "valid-simple-array-primitives":
        assert encode([1, 2, 3]) == expected
    elif sample_name == "valid-simple-array-strings":
        assert encode(["a", "b", "c"]) == expected
    elif sample_name == "valid-simple-array-mixed":
        assert encode([1, "two", True, None]) == expected
    elif sample_name == "valid-simple-array-with-quotes":
        assert encode(["a", "b,c", "d:e"]) == expected
    elif sample_name == "valid-simple-array-tabular":
        assert (
            encode([{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]) == expected
        )
    else:
        # For samples not yet implemented, just verify the file can be loaded
        assert expected is not None, f"Failed to load sample: {sample_name}"
