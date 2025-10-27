"""
Tests for invalid format detection and error handling.

This module tests that the encoder never produces invalid TOON formats
by verifying that encoded output doesn't contain the errors shown in
the invalid sample files.

Tests follow the coding standards defined in docs/CODING_STANDARDS.md:
- Uses type hints throughout
- Comprehensive docstrings with examples
- Single responsibility functions
- Clear, descriptive test names
- Organized test classes by functionality
"""

import pytest

from toon import encode
from tests.sample_data import get_sample


class TestInvalidSimpleScenarios:
    """Test that encoder never produces simple invalid formats."""

    def test_no_trailing_spaces(self) -> None:
        """Test that output never has trailing spaces."""
        # Test various data structures
        test_cases = [
            {"name": "Alice"},
            {"name": "Alice", "age": 30},
            [1, 2, 3],
            ["hello", "world"],
        ]

        for data in test_cases:
            result = encode(data)
            # No line should end with a space
            lines = result.split("\n")
            for line in lines:
                assert not line.endswith(" "), f"Trailing space found in: {repr(line)}"

    def test_no_trailing_newlines(self) -> None:
        """Test that output never ends with a newline."""
        test_cases = [
            None,
            True,
            42,
            "hello",
            {},
            {"name": "Alice"},
            [],
            [1, 2, 3],
        ]

        for data in test_cases:
            result = encode(data)
            assert not result.endswith("\n"), (
                f"Trailing newline found in: {repr(result)}"
            )

    def test_no_odd_indentation(self) -> None:
        """Test that indentation uses consistent spacing."""
        # Test nested structures
        data = {"user": {"profile": {"name": "Alice"}}}
        result = encode(data)

        lines = result.split("\n")
        for line in lines:
            if line.strip():  # Skip empty lines
                # Count leading spaces
                leading_spaces = len(line) - len(line.lstrip())
                # Should be even (0, 2, 4, 6, etc.)
                assert leading_spaces % 2 == 0, f"Odd indentation in: {repr(line)}"

    def test_no_missing_colons(self) -> None:
        """Test that all key-value pairs have colons in non-tabular format."""
        # Test simple key-value pairs that should have colons
        test_cases = [
            ({"name": "Alice"}, ["name: Alice"]),
            ({"user": {"name": "Bob"}}, ["user:", "  name: Bob"]),
        ]

        for data, expected_patterns in test_cases:
            result = encode(data)
            for pattern in expected_patterns:
                assert pattern in result, (
                    f"Expected pattern '{pattern}' not found in: {repr(result)}"
                )

    def test_no_unquoted_special_keys(self) -> None:
        """Test that keys with special characters are quoted."""
        # Keys with special characters should be quoted
        data = {"order:id": 7, "full name": "Alice"}
        result = encode(data)

        # Should contain quotes around special keys
        assert '"order:id"' in result
        assert '"full name"' in result

    def test_no_unquoted_ambiguous_strings(self) -> None:
        """Test that ambiguous strings are quoted."""
        # Strings that look like booleans or numbers should be quoted
        data = {"flag": "true", "count": "42", "status": "null"}
        result = encode(data)

        # Should contain quotes around ambiguous strings
        assert '"true"' in result
        assert '"42"' in result
        assert '"null"' in result

    def test_no_unescaped_newlines(self) -> None:
        """Test that newlines in strings are escaped."""
        data = {"text": "line1\nline2"}
        result = encode(data)

        # Should escape newlines
        assert '"line1\\nline2"' in result

    def test_array_length_matches_content(self) -> None:
        """Test that array length indicators match actual content."""
        test_cases = [
            [1, 2, 3],
            ["a", "b", "c"],
            [1, "two", True, None],
        ]

        for data in test_cases:
            result = encode(data)
            # Should start with correct length
            expected_length = len(data)
            assert result.startswith(f"[{expected_length}]"), (
                f"Wrong length in: {repr(result)}"
            )

    def test_no_trailing_commas_in_arrays(self) -> None:
        """Test that arrays don't have trailing commas."""
        test_cases = [
            [1, 2, 3],
            ["a", "b", "c"],
            [],
        ]

        for data in test_cases:
            result = encode(data)
            # Should not end with comma
            if data:  # Non-empty arrays
                content_part = result.split("]: ", 1)[1] if "]: " in result else ""
                assert not content_part.endswith(","), (
                    f"Trailing comma in: {repr(result)}"
                )

    def test_no_leading_commas_in_arrays(self) -> None:
        """Test that arrays don't have leading commas."""
        test_cases = [
            [1, 2, 3],
            ["a", "b", "c"],
            [],
        ]

        for data in test_cases:
            result = encode(data)
            # Should not start with comma after length indicator
            if data:  # Non-empty arrays
                content_part = result.split("]: ", 1)[1] if "]: " in result else ""
                assert not content_part.startswith(","), (
                    f"Leading comma in: {repr(result)}"
                )

    def test_tabular_format_constraints(self) -> None:
        """Test tabular format constraints."""
        # Uniform objects should use tabular format
        data = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
        result = encode(data)

        # Should use tabular format for uniform objects
        assert "{id,name}:" in result
        assert "Alice" in result
        assert "Bob" in result

        # Non-uniform objects should use list format
        data_mixed = [{"id": 1}, {"id": 2, "name": "Bob"}]
        result_mixed = encode(data_mixed)

        # Should use list format for non-uniform objects
        assert "id: 1" in result_mixed
        assert "- id: 2" in result_mixed

    def test_no_mixed_delimiters(self) -> None:
        """Test that delimiters are used consistently."""
        # Test with different delimiters
        data = [1, 2, 3]

        # Comma delimiter (default)
        result_comma = encode(data, delimiter=",")
        comma_count = result_comma.count(",")
        assert comma_count == 2  # Should have exactly 2 commas for 3 elements

        # Pipe delimiter (appears in length marker AND between elements)
        result_pipe = encode(data, delimiter="|")
        pipe_count = result_pipe.count("|")
        assert pipe_count == 3  # One in [3|] marker, 2 between elements

        # Tab delimiter (appears in length marker AND between elements)
        result_tab = encode(data, delimiter="\t")
        tab_count = result_tab.count("\t")
        assert tab_count == 3  # One in [3\t] marker, 2 between elements

    def test_length_marker_consistency(self) -> None:
        """Test that length markers are used consistently."""
        data = [1, 2, 3]

        # Without length marker
        result_normal = encode(data)
        assert "[3]:" in result_normal
        assert "[#3]" not in result_normal

        # With length marker
        result_marker = encode(data, length_marker="#")
        assert "[#3]:" in result_marker
        assert "[3]" not in result_marker


class TestInvalidComplexScenarios:
    """Test that encoder never produces complex invalid formats."""

    def test_no_broken_nesting(self) -> None:
        """Test that nesting is properly maintained."""
        data = {"level1": {"level2": {"level3": "deep"}}}
        result = encode(data)

        # Should have proper indentation levels
        lines = result.split("\n")
        indent_levels = []
        for line in lines:
            if line.strip():
                indent_level = (len(line) - len(line.lstrip())) // 2
                indent_levels.append(indent_level)

        # Indentation should be strictly increasing then decreasing
        max_indent = max(indent_levels)
        assert indent_levels.count(max_indent) == 1  # Only one line at max depth

    def test_no_extra_blank_lines(self) -> None:
        """Test that there are no unnecessary blank lines."""
        test_cases = [
            {"name": "Alice", "details": {"age": 30, "active": True}},
            {"items": [{"id": 1}, {"id": 2}]},
        ]

        for data in test_cases:
            result = encode(data)
            lines = result.split("\n")

            # No more than one consecutive blank line
            blank_count = 0
            for line in lines:
                if not line.strip():
                    blank_count += 1
                    assert blank_count <= 1, f"Too many blank lines in: {repr(result)}"
                else:
                    blank_count = 0

    def test_no_mixed_indent_levels(self) -> None:
        """Test that indentation levels are consistent."""
        data = {
            "users": [
                {"profile": {"settings": {"theme": "dark"}}},
                {"profile": {"settings": {"theme": "light"}}},
            ]
        }
        result = encode(data)

        lines = result.split("\n")
        indent_sizes = set()

        for line in lines:
            if line.strip():
                indent_size = len(line) - len(line.lstrip())
                indent_sizes.add(indent_size)

        # All indentation should be multiples of 2
        for size in indent_sizes:
            assert size % 2 == 0, f"Non-even indentation: {size} spaces"

    def test_nested_array_length_consistency(self) -> None:
        """Test that nested array lengths are correct."""
        data = {"matrix": [[1, 2, 3], [4, 5]]}
        result = encode(data)

        # Should have correct lengths for nested arrays
        assert "[3]: 1,2,3" in result
        assert "[2]: 4,5" in result

    def test_tabular_row_consistency(self) -> None:
        """Test that tabular rows have consistent column counts."""
        data = {
            "items": [
                {"id": 1, "name": "Alice", "age": 30},
                {"id": 2, "name": "Bob", "age": 25},
                {"id": 3, "name": "Charlie", "age": 35},
            ]
        }
        result = encode(data)

        # Should use tabular format
        assert "{id,name,age}:" in result

        # All rows should have same number of columns
        lines = result.split("\n")
        data_lines = [
            line
            for line in lines
            if line.strip() and not line.startswith("[") and not line.startswith("{")
        ]
        for line in data_lines:
            column_count = line.count(",") + 1
            assert column_count == 3, f"Inconsistent columns in: {repr(line)}"


class TestFormatInvariants:
    """Test formatting invariants that must always be maintained."""

    def test_output_is_deterministic(self) -> None:
        """Test that encoding is deterministic (same input produces same output)."""
        test_cases = [
            {"name": "Alice", "age": 30},
            {"items": [1, 2, 3]},
            {"user": {"profile": {"settings": {"theme": "dark"}}}},
        ]

        for data in test_cases:
            result1 = encode(data)
            result2 = encode(data)
            assert result1 == result2, f"Non-deterministic output for: {data}"

    def test_output_is_valid_toon_format(self) -> None:
        """Test that output conforms to TOON format rules."""
        test_cases = [
            None,
            True,
            42,
            "hello",
            {"name": "Alice"},
            [1, 2, 3],
            {"users": [{"id": 1}, {"id": 2}]},
        ]

        for data in test_cases:
            result = encode(data)

            # Basic format validation
            lines = result.split("\n")
            for line in lines:
                # No trailing spaces
                assert not line.endswith(" "), f"Trailing space in: {repr(line)}"
                # No tabs (unless using tab delimiter)
                if "\t" in line and not result.startswith("["):
                    # Only allow tabs in array length indicators when using tab delimiter
                    assert ": " in line or line.startswith("["), (
                        f"Unexpected tab in: {repr(line)}"
                    )

    def test_options_validation(self) -> None:
        """Test that encoding options are properly validated."""
        data = {"name": "Alice"}

        # Valid options should work
        assert encode(data, indent=1) == "name: Alice"
        assert encode(data, indent=4) == "name: Alice"
        assert encode(data, delimiter=",") == "name: Alice"
        assert encode(data, delimiter="|") == "name: Alice"
        assert encode(data, length_marker=False) == "name: Alice"
        assert encode(data, length_marker="#") == "name: Alice"

        # Invalid options should raise errors
        with pytest.raises(ValueError):  # Should raise ValidationError from Pydantic
            encode(data, indent=-1)

        with pytest.raises(ValueError):  # indent=0 is not supported
            encode(data, indent=0)

    def test_edge_case_handling(self) -> None:
        """Test edge cases and boundary conditions."""
        # Empty structures
        assert encode({}) == ""
        assert encode([]) == "[0]:"

        # Single element structures
        assert encode({"key": "value"}) == "key: value"
        assert encode(["item"]) == "[1]: item"

        # Deep nesting
        deep_data = {"a": {"b": {"c": {"d": {"e": "deep"}}}}}
        result = encode(deep_data)
        assert "deep" in result

        # Wide structures
        wide_data = {f"key_{i}": f"value_{i}" for i in range(10)}
        result = encode(wide_data)
        assert len(result.split("\n")) == 10


# Parameterized tests for all invalid samples
INVALID_SIMPLE_SAMPLES = [
    "invalid-simple-trailing-space",
    "invalid-simple-trailing-newline",
    "invalid-simple-wrong-indent",
    "invalid-simple-odd-indent-spaces",
    "invalid-simple-missing-colon",
    "invalid-simple-missing-key",
    "invalid-simple-unquoted-special-key",
    "invalid-simple-unquoted-comma-value",
    "invalid-simple-ambiguous-string-unquoted",
    "invalid-simple-unescaped-newline",
    "invalid-simple-array-missing-colon",
    "invalid-simple-array-wrong-length",
    "invalid-simple-array-trailing-comma",
    "invalid-simple-array-leading-comma",
    "invalid-simple-array-spaces-after-delimiter",
    "invalid-simple-array-unquoted-structural",
    "invalid-simple-tabular-missing-colon",
    "invalid-simple-tabular-missing-indent",
    "invalid-simple-tabular-wrong-column-count",
    "invalid-simple-tabular-wrong-row-count",
    "invalid-simple-tabular-header-no-comma",
    "invalid-simple-list-missing-colon",
    "invalid-simple-list-missing-hyphen",
    "invalid-simple-list-hyphen-no-space",
    "invalid-simple-list-wrong-continuation-indent",
    "invalid-simple-mixed-delimiters",
    "invalid-simple-length-marker-mismatch",
]


@pytest.mark.parametrize("sample_name", INVALID_SIMPLE_SAMPLES)
def test_encoder_never_produces_invalid_simple_formats(sample_name: str) -> None:
    """
    Test that encoder never produces any of the invalid simple formats.

    This parameterized test ensures that the encoder output never matches
    any of the invalid simple sample files, meaning it never produces
    the format violations shown in those samples.

    Args:
        sample_name: Name of the invalid sample file to test against
    """
    invalid_content = get_sample(sample_name)

    # Test various valid data structures
    test_data = [
        None,
        True,
        False,
        42,
        3.14,
        "hello",
        "hello world",
        {"name": "Alice"},
        {"order:id": 7},
        {"note": "a,b"},
        [1, 2, 3],
        ["a", "b,c", "true"],
        [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}],
    ]

    for data in test_data:
        result = encode(data)
        # Encoder output should never match invalid format
        assert result != invalid_content, f"Encoder produced invalid format for {data}"


# Parameterized tests for all invalid complex samples
INVALID_COMPLEX_SAMPLES = [
    "invalid-complex-nested-trailing-space",
    "invalid-complex-broken-nesting",
    "invalid-complex-extra-blank-lines",
    "invalid-complex-mixed-indent-levels",
    "invalid-complex-mixed-list-structure-error",
    "invalid-complex-tabular-length-mismatch",
    "invalid-complex-tabular-inconsistent-columns",
    "invalid-complex-tabular-wrong-row-indent",
    "invalid-complex-tabular-inconsistent-header-quoting",
    "invalid-complex-tabular-quoted-row-as-single",
    "invalid-complex-tabular-unquoted-special-value",
    "invalid-complex-nested-tabular-wrong-indent",
    "invalid-complex-list-indent-mismatch",
    "invalid-complex-list-missing-hyphen-continuation",
    "invalid-complex-nested-array-wrong-length",
    "invalid-complex-nested-array-length-mismatch",
    "invalid-complex-root-array-length-mismatch",
    "invalid-complex-deeply-nested-length-error",
    "invalid-complex-delimiter-inconsistency",
    "invalid-complex-length-marker-inconsistency",
]


@pytest.mark.parametrize("sample_name", INVALID_COMPLEX_SAMPLES)
def test_encoder_never_produces_invalid_complex_formats(sample_name: str) -> None:
    """
    Test that encoder never produces any of the invalid complex formats.

    This parameterized test ensures that the encoder output never matches
    any of the invalid complex sample files, meaning it never produces
    the format violations shown in those samples.

    Args:
        sample_name: Name of the invalid sample file to test against
    """
    invalid_content = get_sample(sample_name)

    # Test various complex data structures
    test_data = [
        {"user": {"name": "Alice", "tags": ["admin", "user"]}},
        {"items": [{"id": 1}, {"id": 2, "name": "Bob"}]},
        {"matrix": [[1, 2], [3, 4]]},
        {"deep": {"nested": {"structure": {"value": "test"}}}},
        {"mixed": [1, {"key": "value"}, "text"]},
    ]

    for data in test_data:
        result = encode(data)
        # Encoder output should never match invalid format
        assert result != invalid_content, f"Encoder produced invalid format for {data}"
