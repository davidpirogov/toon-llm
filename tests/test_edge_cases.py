"""
Tests for edge cases and boundary conditions.

This module tests edge cases, boundary conditions, and special scenarios
that may not be covered by the main test suites but are important for
robustness and correctness.

Tests follow the coding standards defined in docs/CODING_STANDARDS.md:
- Uses type hints throughout
- Comprehensive docstrings with examples
- Single responsibility functions
- Clear, descriptive test names
- Organized test classes by functionality
"""

import pytest
from datetime import datetime, timezone
from dataclasses import dataclass
from typing import Any

from toon import encode
# Sample data utilities available if needed


class TestPrimitiveEdgeCases:
    """Test edge cases for primitive value encoding."""

    def test_zero_values(self) -> None:
        """Test encoding of zero values."""
        assert encode(0) == "0"
        assert encode(0.0) == "0"
        assert encode(-0) == "0"  # Negative zero should become positive

    def test_scientific_notation(self) -> None:
        """Test encoding of scientific notation numbers."""
        assert encode(1e6) == "1000000"
        assert encode(1e-6) == "0.000001"
        assert encode(1.5e10) == "15000000000"

    def test_non_finite_numbers(self) -> None:
        """Test encoding of non-finite numbers."""
        assert encode(float("inf")) == "null"
        assert encode(float("-inf")) == "null"
        assert encode(float("nan")) == "null"

    def test_very_large_numbers(self) -> None:
        """Test encoding of very large numbers."""
        large_int = 999999999999999999999999999999999999
        result = encode(large_int)
        assert result == str(large_int)

    def test_very_small_numbers(self) -> None:
        """Test encoding of very small numbers."""
        small_float = 1e-100
        result = encode(small_float)
        assert result == str(small_float)

    def test_unicode_strings(self) -> None:
        """Test encoding of various unicode strings."""
        test_cases = [
            ("café", "café"),
            ("你好", "你好"),
            ("🚀", "🚀"),
            ("hello 👋 world", "hello 👋 world"),
            ("αβγδε", "αβγδε"),
            ("русский", "русский"),
        ]

        for input_str, expected in test_cases:
            assert encode(input_str) == expected

    def test_empty_and_whitespace_strings(self) -> None:
        """Test encoding of empty and whitespace strings."""
        assert encode("") == '""'
        assert encode(" ") == '" "'
        assert encode("  ") == '"  "'
        assert encode("\t") == '"\\t"'
        assert encode("\n") == '"\\n"'


class TestObjectEdgeCases:
    """Test edge cases for object encoding."""

    def test_empty_object(self) -> None:
        """Test encoding of empty object."""
        assert encode({}) == ""

    def test_single_key_object(self) -> None:
        """Test encoding of single key object."""
        assert encode({"key": "value"}) == "key: value"

    def test_numeric_keys(self) -> None:
        """Test encoding of numeric keys."""
        assert encode({123: "value"}) == '"123": value'

    def test_empty_string_key(self) -> None:
        """Test encoding of empty string key."""
        assert encode({"": "value"}) == '"": value'

    def test_deeply_nested_objects(self) -> None:
        """Test encoding of deeply nested objects."""
        data = {"a": {"b": {"c": {"d": {"e": {"f": {"g": "deep"}}}}}}}
        result = encode(data)
        assert "deep" in result

        # Check proper indentation
        lines = result.split("\n")
        assert len(lines) == 7  # 7 levels of nesting

    def test_wide_objects(self) -> None:
        """Test encoding of objects with many keys."""
        data = {f"key_{i}": f"value_{i}" for i in range(100)}
        result = encode(data)

        # Should have 100 lines
        lines = result.split("\n")
        assert len(lines) == 100

        # All keys should be present
        for i in range(100):
            assert f"key_{i}: value_{i}" in result

    def test_mixed_key_types(self) -> None:
        """Test encoding of objects with mixed key types."""
        data = {"string_key": "value1", 123: "value2", True: "value3", None: "value4"}
        result = encode(data)

        # String keys should be unquoted, others quoted
        assert "string_key: value1" in result
        assert '"123": value2' in result
        assert '"True": value3' in result
        assert '"None": value4' in result


class TestArrayEdgeCases:
    """Test edge cases for array encoding."""

    def test_empty_array(self) -> None:
        """Test encoding of empty array."""
        assert encode([]) == "[0]:"

    def test_single_element_array(self) -> None:
        """Test encoding of single element array."""
        assert encode([42]) == "[1]: 42"
        assert encode(["hello"]) == "[1]: hello"

    def test_large_arrays(self) -> None:
        """Test encoding of large arrays."""
        data = list(range(1000))
        result = encode(data)

        # Should start with correct length
        assert result.startswith("[1000]:")
        # Should contain all elements
        for i in range(1000):
            assert str(i) in result

    def test_nested_empty_arrays(self) -> None:
        """Test encoding of nested empty arrays."""
        data = [[], [], []]
        result = encode(data)
        assert "[3]:" in result
        assert "[0]:" in result

    def test_array_of_empty_objects(self) -> None:
        """Test encoding of array of empty objects."""
        data = [{}, {}, {}]
        result = encode(data)
        # Should use list format since objects are empty (different from uniform)
        assert "id: 1" not in result  # Should not use tabular format

    def test_array_of_identical_empty_objects(self) -> None:
        """Test encoding of array of identical empty objects."""
        data = [{}, {}, {}]
        result = encode(data)
        # Should use list format for empty objects
        assert result.count("- ") == 3


class TestComplexDataTypes:
    """Test edge cases for complex data type normalization."""

    def test_datetime_encoding(self) -> None:
        """Test encoding of datetime objects."""
        dt = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        result = encode(dt)
        assert "2024-01-01T12:00:00" in result

        # Naive datetime should be treated as UTC
        dt_naive = datetime(2024, 1, 1, 12, 0, 0)
        result_naive = encode(dt_naive)
        assert "2024-01-01T12:00:00" in result_naive

    def test_dataclass_encoding(self) -> None:
        """Test encoding of dataclass objects."""

        @dataclass
        class Person:
            name: str
            age: int

        person = Person("Alice", 30)
        result = encode(person)
        assert "name: Alice" in result
        assert "age: 30" in result

    def test_set_encoding(self) -> None:
        """Test encoding of set objects."""
        data = {3, 1, 4, 5}  # Should be sorted
        result = encode(data)
        assert "[4]: 1,3,4,5" in result  # Sorted order, 4 elements

    def test_tuple_encoding(self) -> None:
        """Test encoding of tuple objects."""
        data = (1, 2, 3)
        result = encode(data)
        assert "[3]: 1,2,3" in result

    def test_nested_collections(self) -> None:
        """Test encoding of nested collections."""
        data = {"sets": [{1, 2, 3}, {4, 5, 6}]}
        result = encode(data)
        # Sets should be converted to sorted lists
        assert "[3]: 1,2,3" in result
        assert "[3]: 4,5,6" in result


class TestOptionsEdgeCases:
    """Test edge cases for encoding options."""

    def test_zero_indent(self) -> None:
        """Test that zero indentation is rejected."""
        data = {"user": {"name": "Alice"}}
        with pytest.raises(Exception) as exc_info:
            encode(data, indent=0)
        assert "greater than or equal to 1" in str(exc_info.value)

    def test_minimum_indent(self) -> None:
        """Test encoding with minimum indentation (indent=1)."""
        data = {"user": {"name": "Alice"}}
        result = encode(data, indent=1)
        assert result == "user:\n name: Alice"

    def test_large_indent(self) -> None:
        """Test encoding with large indentation."""
        data = {"user": {"name": "Alice"}}
        result = encode(data, indent=10)
        assert result == "user:\n          name: Alice"

    def test_custom_delimiter_edge_cases(self) -> None:
        """Test custom delimiters with edge cases."""
        data = [1, 2, 3]

        # Tab delimiter
        result_tab = encode(data, delimiter="\t")
        assert "[3\t]: 1\t2\t3" in result_tab

        # Pipe delimiter
        result_pipe = encode(data, delimiter="|")
        assert "[3|]: 1|2|3" in result_pipe

        # Multi-character delimiter (if supported)
        # Note: Current implementation may not support multi-char delimiters

    def test_length_marker_edge_cases(self) -> None:
        """Test length marker edge cases."""
        data = [1, 2, 3]

        # With length marker
        result_marker = encode(data, length_marker="#")
        assert "[#3]: 1,2,3" in result_marker

        # Without length marker
        result_no_marker = encode(data, length_marker=False)
        assert "[3]: 1,2,3" in result_no_marker

    def test_combined_options_edge_cases(self) -> None:
        """Test combined options edge cases."""
        data = {"items": [{"name": "Alice"}, {"name": "Bob"}]}

        # Tab delimiter with length marker
        result = encode(data, delimiter="\t", length_marker="#")
        assert "[#2\t]{" in result
        assert "Alice" in result and "Bob" in result


class TestNormalizationEdgeCases:
    """Test edge cases for data normalization."""

    def test_circular_reference_protection(self) -> None:
        """Test that circular references are handled gracefully."""
        # This would typically cause infinite recursion without protection
        data: dict[str, Any] = {"name": "test"}
        data["self"] = data  # Circular reference

        # Should not cause infinite recursion
        result = encode(data)
        assert "name: test" in result

    def test_very_deep_recursion(self) -> None:
        """Test handling of very deep recursion."""
        # Create a deeply nested structure
        data: dict[str, Any] = {"value": "deep"}
        current = data
        for i in range(100):  # Very deep nesting
            current["next"] = {"value": f"level_{i}"}
            current = current["next"]

        result = encode(data)
        assert "deep" in result

    def test_mixed_data_types(self) -> None:
        """Test encoding of mixed data types."""
        data = {
            "primitives": [None, True, False, 42, 3.14, "hello"],
            "collections": [[], {}, [1, 2], {"a": "b"}],
            "special": datetime(2024, 1, 1),
        }
        result = encode(data)

        # Should handle all types correctly
        assert "null" in result
        assert "true" in result
        assert "false" in result
        assert "42" in result
        assert "3.14" in result
        assert "hello" in result
        assert "[0]:" in result
        assert "[2]: 1,2" in result
        assert "a: b" in result


class TestFormatValidation:
    """Test format validation and invariants."""

    def test_no_trailing_spaces_anywhere(self) -> None:
        """Test that no line has trailing spaces."""
        test_cases = [
            None,
            "hello",
            {"name": "Alice", "details": {"age": 30}},
            [1, 2, 3],
            {"items": [{"id": 1}, {"id": 2}]},
        ]

        for data in test_cases:
            result = encode(data)
            lines = result.split("\n")
            for line in lines:
                assert not line.endswith(" "), f"Trailing space in: {repr(line)}"

    def test_no_trailing_newlines(self) -> None:
        """Test that output never ends with newline."""
        test_cases = [
            None,
            "hello",
            {"name": "Alice"},
            [1, 2, 3],
            {"deep": {"nested": {"structure": "value"}}},
        ]

        for data in test_cases:
            result = encode(data)
            assert not result.endswith("\n"), f"Trailing newline in: {repr(result)}"

    def test_consistent_indentation(self) -> None:
        """Test that indentation is consistent throughout."""
        data = {"level1": {"level2": {"level3": {"level4": "deep"}}}}
        result = encode(data)

        lines = result.split("\n")
        for line in lines:
            if line.strip():
                indent_level = len(line) - len(line.lstrip())
                # Indentation should be even (multiples of 2)
                assert indent_level % 2 == 0, f"Odd indentation: {indent_level} spaces"

    def test_deterministic_output(self) -> None:
        """Test that output is deterministic."""
        test_cases = [
            {"b": 1, "a": 2},  # Dict ordering should be preserved
            {"items": [3, 1, 2]},  # List ordering should be preserved
            {"nested": {"z": 1, "y": 2}},  # Nested dict ordering
        ]

        for data in test_cases:
            result1 = encode(data)
            result2 = encode(data)
            assert result1 == result2, f"Non-deterministic output for: {data}"

    def test_key_order_preservation(self) -> None:
        """Test that key order is preserved in objects."""
        data = {"z": 1, "a": 2, "m": 3}
        result = encode(data)

        # Keys should appear in insertion order
        assert "z: 1" in result
        assert "a: 2" in result
        assert "m: 3" in result

        # Check that the first key appears first in the output
        lines = result.split("\n")
        assert lines[0] == "z: 1"


class TestErrorHandling:
    """Test error handling and validation."""

    def test_invalid_indent_values(self) -> None:
        """Test handling of invalid indent values."""
        data = {"name": "Alice"}

        # Negative indent should raise error
        with pytest.raises(ValueError, match="indent"):
            encode(data, indent=-1)

        # Very large indent should work but be unusual
        result = encode(data, indent=100)
        assert "name: Alice" in result

    def test_none_values_in_collections(self) -> None:
        """Test handling of None values in collections."""
        data = {"items": [1, None, 3]}
        result = encode(data)
        assert "null" in result

    def test_mixed_none_and_other_values(self) -> None:
        """Test mixed None and other values."""
        data = {"values": [None, "text", None, 42, None]}
        result = encode(data)
        assert result.count("null") == 3


class TestPerformanceEdgeCases:
    """Test performance-related edge cases."""

    def test_very_long_strings(self) -> None:
        """Test encoding of very long strings."""
        long_string = "x" * 10000
        result = encode(long_string)
        assert result == long_string  # Should not be quoted

        # String with special chars should be quoted
        long_quoted = "x" * 1000 + ","
        result_quoted = encode(long_quoted)
        assert result_quoted.startswith('"') and result_quoted.endswith('"')

    def test_very_nested_structures(self) -> None:
        """Test encoding of very nested structures."""
        # Create a very deeply nested structure
        data: dict[str, Any] = {"value": "root"}
        current = data
        for i in range(50):  # 50 levels deep
            current["child"] = {"value": f"level_{i}"}
            current = current["child"]

        result = encode(data)
        assert "root" in result
        assert "level_49" in result

    def test_very_wide_structures(self) -> None:
        """Test encoding of very wide structures."""
        # Create a very wide object
        data = {f"key_{i:03d}": f"value_{i}" for i in range(1000)}
        result = encode(data)

        # Should handle all keys
        assert len(result.split("\n")) == 1000
        for i in range(1000):
            assert f"key_{i:03d}: value_{i}" in result
