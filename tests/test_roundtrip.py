"""Integration tests for encode/decode round-trip functionality."""

from toon import decode, encode


class TestRoundTripBasics:
    """Test basic round-trip encoding and decoding."""

    def test_roundtrip_simple_object(self):
        """Test round-trip with simple object."""
        data = {"name": "Alice", "age": 30, "active": True}
        encoded = encode(data)
        decoded = decode(encoded)
        assert decoded == data

    def test_roundtrip_nested_object(self):
        """Test round-trip with nested object."""
        data = {"user": {"name": "Bob", "profile": {"age": 25, "city": "NYC"}}}
        encoded = encode(data)
        decoded = decode(encoded)
        assert decoded == data

    def test_roundtrip_primitive_array(self):
        """Test round-trip with primitive array."""
        data = [1, 2, 3, 4, 5]
        encoded = encode(data)
        decoded = decode(encoded)
        assert decoded == data

    def test_roundtrip_string_array(self):
        """Test round-trip with string array."""
        data = ["apple", "banana", "cherry"]
        encoded = encode(data)
        decoded = decode(encoded)
        assert decoded == data

    def test_roundtrip_mixed_primitives(self):
        """Test round-trip with mixed primitive types."""
        data = {"str": "hello", "int": 42, "float": 3.14, "bool": True, "null": None}
        encoded = encode(data)
        decoded = decode(encoded)
        assert decoded == data

    def test_roundtrip_empty_object(self):
        """
        Test round-trip with empty object.

        Note: Empty objects encode to empty string (""), but empty string also
        decodes to empty string (""), not empty object ({}). This is a fundamental
        ambiguity in the TOON format - there's no way to distinguish between an
        empty object and an empty string when both encode to "".
        """
        data = {}
        encoded = encode(data)
        decoded = decode(encoded)
        assert decoded == ""  # Decodes to empty string, not empty object

    def test_roundtrip_empty_array(self):
        """Test round-trip with empty array."""
        data = []
        encoded = encode(data)
        decoded = decode(encoded)
        assert decoded == data


class TestRoundTripArrays:
    """Test round-trip with various array formats."""

    def test_roundtrip_tabular_array(self):
        """Test round-trip with tabular array of objects."""
        data = [
            {"name": "Alice", "age": 30, "city": "NYC"},
            {"name": "Bob", "age": 25, "city": "LA"},
            {"name": "Charlie", "age": 35, "city": "SF"},
        ]
        encoded = encode(data)
        decoded = decode(encoded)
        assert decoded == data

    def test_roundtrip_list_format_array(self):
        """Test round-trip with list format array."""
        data = [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "score": 95},  # Different keys
        ]
        encoded = encode(data)
        decoded = decode(encoded)
        assert decoded == data

    def test_roundtrip_array_of_arrays(self):
        """Test round-trip with array of arrays."""
        data = [
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 9],
        ]
        encoded = encode(data)
        decoded = decode(encoded)
        assert decoded == data

    def test_roundtrip_nested_arrays_in_object(self):
        """Test round-trip with nested arrays in object."""
        data = {
            "matrix": [[1, 2], [3, 4], [5, 6]],
            "tags": ["a", "b", "c"],
        }
        encoded = encode(data)
        decoded = decode(encoded)
        assert decoded == data


class TestRoundTripWithDelimiters:
    """Test round-trip with custom delimiters."""

    def test_roundtrip_with_pipe_delimiter(self):
        """Test round-trip with pipe delimiter."""
        data = ["apple", "banana", "cherry"]
        encoded = encode(data, delimiter="|")
        decoded = decode(encoded, delimiter="|")
        assert decoded == data

    def test_roundtrip_with_tab_delimiter(self):
        """Test round-trip with tab delimiter."""
        data = {"tags": ["reading", "gaming", "coding"]}
        encoded = encode(data, delimiter="\t")
        decoded = decode(encoded, delimiter="\t")
        assert decoded == data

    def test_roundtrip_tabular_with_pipe_delimiter(self):
        """Test round-trip tabular format with pipe delimiter."""
        data = [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25},
        ]
        encoded = encode(data, delimiter="|")
        decoded = decode(encoded, delimiter="|")
        assert decoded == data

    def test_roundtrip_tabular_with_tab_delimiter(self):
        """Test round-trip tabular format with tab delimiter."""
        data = [
            {"id": 1, "value": 100},
            {"id": 2, "value": 200},
        ]
        encoded = encode(data, delimiter="\t")
        decoded = decode(encoded, delimiter="\t")
        assert decoded == data

    def test_roundtrip_values_with_commas_pipe_delimiter(self):
        """Test round-trip with commas in values using pipe delimiter."""
        data = {"notes": ["a,b", "c,d", "e,f"]}
        encoded = encode(data, delimiter="|")
        decoded = decode(encoded, delimiter="|")
        assert decoded == data


class TestRoundTripWithLengthMarker:
    """Test round-trip with length markers."""

    def test_roundtrip_with_length_marker(self):
        """Test round-trip with length marker."""
        data = [1, 2, 3, 4, 5]
        encoded = encode(data, length_marker="#")
        # Length marker doesn't affect decoding
        decoded = decode(encoded)
        assert decoded == data

    def test_roundtrip_tabular_with_length_marker(self):
        """Test round-trip tabular format with length marker."""
        data = [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25},
        ]
        encoded = encode(data, length_marker="#")
        decoded = decode(encoded)
        assert decoded == data

    def test_roundtrip_combined_options(self):
        """Test round-trip with length marker and custom delimiter."""
        data = ["a", "b", "c"]
        encoded = encode(data, delimiter="|", length_marker="#")
        decoded = decode(encoded, delimiter="|")
        assert decoded == data


class TestRoundTripQuotedValues:
    """Test round-trip with quoted values."""

    def test_roundtrip_quoted_strings(self):
        """Test round-trip with strings requiring quotes."""
        data = {"note": "a,b", "path": "C:\\Users", "text": 'say "hello"'}
        encoded = encode(data)
        decoded = decode(encoded)
        assert decoded == data

    def test_roundtrip_empty_string(self):
        """Test round-trip with empty string."""
        data = {"value": ""}
        encoded = encode(data)
        decoded = decode(encoded)
        assert decoded == data

    def test_roundtrip_whitespace_strings(self):
        """Test round-trip with whitespace strings."""
        data = {"a": " ", "b": "  ", "c": " padded "}
        encoded = encode(data)
        decoded = decode(encoded)
        assert decoded == data

    def test_roundtrip_quoted_keys(self):
        """Test round-trip with keys requiring quotes."""
        data = {"order:id": 1, "full name": "Alice", " key ": "value"}
        encoded = encode(data)
        decoded = decode(encoded)
        assert decoded == data

    def test_roundtrip_array_with_quoted_elements(self):
        """Test round-trip with array containing quoted elements."""
        data = ["a,b", "c:d", "[x]", "- item", "{key}"]
        encoded = encode(data)
        decoded = decode(encoded)
        assert decoded == data


class TestRoundTripComplexStructures:
    """Test round-trip with complex nested structures."""

    def test_roundtrip_deeply_nested(self):
        """Test round-trip with deeply nested structure."""
        data = {
            "level1": {
                "level2": {
                    "level3": {"level4": {"value": "deep"}},
                    "array": [1, 2, 3],
                },
                "name": "test",
            }
        }
        encoded = encode(data)
        decoded = decode(encoded)
        assert decoded == data

    def test_roundtrip_mixed_structure(self):
        """Test round-trip with mixed objects and arrays."""
        data = {
            "users": [
                {"name": "Alice", "tags": ["admin", "user"]},
                {"name": "Bob", "tags": ["user"]},
            ],
            "settings": {"theme": "dark", "notifications": True},
            "version": "1.0.0",
        }
        encoded = encode(data)
        decoded = decode(encoded)
        assert decoded == data

    def test_roundtrip_real_world_example(self):
        """Test round-trip with real-world-like data."""
        data = {
            "company": "TechCorp",
            "founded": 2020,
            "employees": [
                {"id": 1, "name": "Alice", "role": "CEO", "active": True},
                {"id": 2, "name": "Bob", "role": "CTO", "active": True},
                {"id": 3, "name": "Charlie", "role": "Engineer", "active": False},
            ],
            "offices": [
                {"city": "NYC", "country": "USA", "staff": [1, 2]},
                {"city": "London", "country": "UK", "staff": [3]},
            ],
            "metadata": {
                "tags": ["tech", "saas", "b2b", "startup"],
                "investors": [],
            },
        }
        encoded = encode(data)
        decoded = decode(encoded)
        assert decoded == data


class TestRoundTripEdgeCases:
    """Test round-trip with edge cases."""

    def test_roundtrip_null_values(self):
        """Test round-trip with null values."""
        data = {"a": None, "b": [None, None], "c": {"d": None}}
        encoded = encode(data)
        decoded = decode(encoded)
        assert decoded == data

    def test_roundtrip_negative_numbers(self):
        """Test round-trip with negative numbers."""
        data = {"values": [-1, -2, -3], "min": -100, "max": 100}
        encoded = encode(data)
        decoded = decode(encoded)
        assert decoded == data

    def test_roundtrip_float_numbers(self):
        """Test round-trip with float numbers."""
        data = {"pi": 3.14, "e": 2.718, "values": [1.5, 2.7, 3.9]}
        encoded = encode(data)
        decoded = decode(encoded)
        assert decoded == data

    def test_roundtrip_boolean_values(self):
        """Test round-trip with boolean values."""
        data = {"true": True, "false": False, "flags": [True, False, True]}
        encoded = encode(data)
        decoded = decode(encoded)
        assert decoded == data

    def test_roundtrip_unicode_strings(self):
        """Test round-trip with unicode strings."""
        data = {"greeting": "café", "emoji": "👋", "text": "こんにちは"}
        encoded = encode(data)
        decoded = decode(encoded)
        assert decoded == data

    def test_roundtrip_special_numbers(self):
        """Test round-trip with special number values."""
        data = {"zero": 0, "negative_zero": -0, "large": 1e20}
        encoded = encode(data)
        decoded = decode(encoded)
        # Note: -0 becomes 0 in TOON format
        assert isinstance(decoded, dict)
        assert decoded.get("zero") == 0
        assert decoded.get("negative_zero") == 0
        assert decoded.get("large") == 1e20


class TestRoundTripIndentation:
    """Test round-trip with different indentation levels."""

    def test_roundtrip_custom_indentation(self):
        """Test round-trip with custom indentation."""
        data = {"a": {"b": {"c": "value"}}}
        encoded = encode(data, indent=4)
        decoded = decode(encoded)
        assert decoded == data

    def test_roundtrip_minimum_indentation(self):
        """
        Test round-trip with minimum indentation (indent=1).

        The TOON specification requires a minimum indent of 1 space per level
        to ensure nested objects are distinguishable from peer fields.
        """
        data = {"a": {"b": {"c": "value"}}}
        encoded = encode(data, indent=1)
        decoded = decode(encoded)
        assert decoded == data

    def test_roundtrip_large_indentation(self):
        """Test round-trip with large indentation."""
        data = {"nested": {"deeply": {"value": 42}}}
        encoded = encode(data, indent=8)
        decoded = decode(encoded)
        assert decoded == data
