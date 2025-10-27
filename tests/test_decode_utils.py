"""Tests for utils.decode function."""

import pytest

from pytoon import decode
from pytoon.errors import DecodeError


class TestDecodeBasics:
    """Test basic decode functionality."""

    def test_decode_empty_string(self):
        """Test decoding an empty string."""
        result = decode("")
        assert result == ""

    def test_decode_simple_object(self):
        """Test decoding a simple object."""
        text = "name: Alice\nage: 30"
        result = decode(text)
        assert result == {"name": "Alice", "age": 30}

    def test_decode_nested_object(self):
        """Test decoding a nested object."""
        text = "user:\n  name: Bob\n  age: 25"
        result = decode(text)
        assert result == {"user": {"name": "Bob", "age": 25}}

    def test_decode_primitive_string(self):
        """Test decoding a simple string."""
        result = decode("hello")
        assert result == "hello"

    def test_decode_primitive_number(self):
        """Test decoding a number."""
        result = decode("42")
        assert result == 42

    def test_decode_primitive_boolean(self):
        """Test decoding booleans."""
        assert decode("true") is True
        assert decode("false") is False

    def test_decode_primitive_null(self):
        """Test decoding null."""
        result = decode("null")
        assert result is None


class TestDecodeArrays:
    """Test decode functionality for arrays."""

    def test_decode_inline_array(self):
        """Test decoding inline array."""
        result = decode("[3]: 1,2,3")
        assert result == [1, 2, 3]

    def test_decode_empty_array(self):
        """Test decoding empty array."""
        result = decode("[0]:")
        assert result == []

    def test_decode_array_with_strings(self):
        """Test decoding array with strings."""
        result = decode("[3]: a,b,c")
        assert result == ["a", "b", "c"]

    def test_decode_array_in_object(self):
        """Test decoding array as object field."""
        text = "tags[2]: reading,gaming"
        result = decode(text)
        assert result == {"tags": ["reading", "gaming"]}

    def test_decode_tabular_array(self):
        """Test decoding tabular array."""
        text = "[2]{name,age}:\nAlice,30\nBob,25"
        result = decode(text)
        assert result == [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25},
        ]

    def test_decode_list_format_array(self):
        """Test decoding list format array."""
        text = "[2]:\n- name: Alice\n  age: 30\n- name: Bob\n  age: 25"
        result = decode(text)
        assert result == [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25},
        ]

    def test_decode_array_of_arrays(self):
        """Test decoding array of arrays."""
        text = "[2]:\n- [2]: a,b\n- [2]: c,d"
        result = decode(text)
        assert result == [["a", "b"], ["c", "d"]]


class TestDecodeWithDelimiters:
    """Test decode with custom delimiters."""

    def test_decode_with_pipe_delimiter(self):
        """Test decoding with pipe delimiter."""
        text = "[3|]: a|b|c"
        result = decode(text, delimiter="|")
        assert result == ["a", "b", "c"]

    def test_decode_with_tab_delimiter(self):
        """Test decoding with tab delimiter."""
        text = "[3\t]: a\tb\tc"
        result = decode(text, delimiter="\t")
        assert result == ["a", "b", "c"]

    def test_decode_tabular_with_pipe_delimiter(self):
        """Test decoding tabular format with pipe delimiter."""
        text = "[2|]{name|age}:\nAlice|30\nBob|25"
        result = decode(text, delimiter="|")
        assert result == [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25},
        ]

    def test_decode_tabular_with_tab_delimiter(self):
        """Test decoding tabular format with tab delimiter."""
        text = "[2\t]{name\tage}:\nAlice\t30\nBob\t25"
        result = decode(text, delimiter="\t")
        assert result == [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25},
        ]

    def test_decode_comma_in_value_with_pipe_delimiter(self):
        """Test that commas in values work with pipe delimiter."""
        text = "[2|]: a,b|c,d"
        result = decode(text, delimiter="|")
        assert result == ["a,b", "c,d"]


class TestDecodeQuotedValues:
    """Test decode with quoted values."""

    def test_decode_quoted_string(self):
        """Test decoding quoted string."""
        result = decode('"hello world"')
        assert result == "hello world"

    def test_decode_empty_quoted_string(self):
        """Test decoding empty quoted string."""
        result = decode('""')
        assert result == ""

    def test_decode_quoted_value_in_object(self):
        """Test decoding quoted value in object."""
        text = 'note: "a,b"'
        result = decode(text)
        assert result == {"note": "a,b"}

    def test_decode_quoted_key(self):
        """Test decoding quoted key."""
        text = '"order:id": 7'
        result = decode(text)
        assert result == {"order:id": 7}

    def test_decode_quoted_array_element(self):
        """Test decoding quoted array element."""
        text = '[3]: a,"b,c",d'
        result = decode(text)
        assert result == ["a", "b,c", "d"]

    def test_decode_escaped_quotes(self):
        """Test decoding escaped quotes in strings."""
        text = r'text: "say \"hello\""'
        result = decode(text)
        assert result == {"text": 'say "hello"'}


class TestDecodeEdgeCases:
    """Test edge cases and error handling."""

    def test_decode_object_with_null_value(self):
        """Test decoding object with null value."""
        text = "name: null"
        result = decode(text)
        assert result == {"name": None}

    def test_decode_whitespace_only(self):
        """Test decoding whitespace only."""
        result = decode("   \n  \n  ")
        assert result == ""

    def test_decode_quoted_whitespace(self):
        """Test decoding quoted whitespace."""
        text = 'value: "  "'
        result = decode(text)
        assert result == {"value": "  "}

    def test_decode_negative_numbers(self):
        """Test decoding negative numbers."""
        text = "[3]: -1,-2,-3"
        result = decode(text)
        assert result == [-1, -2, -3]

    def test_decode_float_numbers(self):
        """Test decoding float numbers."""
        text = "[3]: 1.5,2.7,3.9"
        result = decode(text)
        assert result == [1.5, 2.7, 3.9]


class TestDecodeErrors:
    """Test error handling in decode."""

    def test_decode_invalid_array_length(self):
        """Test that invalid array length raises error."""
        text = "[3]: 1,2"  # Length says 3 but only 2 items
        with pytest.raises(DecodeError):
            decode(text)

    def test_decode_invalid_tabular_row_count(self):
        """Test that invalid tabular row count raises error."""
        text = "[3]{name,age}:\nAlice,30\nBob,25"  # Says 3 rows but only 2
        with pytest.raises(DecodeError):
            decode(text)

    def test_decode_invalid_array_header(self):
        """Test that invalid array header raises error."""
        text = "[abc]: 1,2,3"  # Non-numeric length
        with pytest.raises(DecodeError):
            decode(text)


class TestDecodeComplexStructures:
    """Test decoding complex nested structures."""

    def test_decode_deeply_nested_object(self):
        """Test decoding deeply nested object."""
        text = "a:\n  b:\n    c:\n      d: value"
        result = decode(text)
        assert result == {"a": {"b": {"c": {"d": "value"}}}}

    def test_decode_mixed_structure(self):
        """Test decoding mixed structure with objects and arrays."""
        text = """user:
  name: Alice
  tags[2]: reading,gaming
  prefs:
    theme: dark"""
        result = decode(text)
        assert result == {
            "user": {
                "name": "Alice",
                "tags": ["reading", "gaming"],
                "prefs": {"theme": "dark"},
            }
        }

    def test_decode_nested_tabular_arrays(self):
        """Test decoding nested tabular arrays."""
        text = """[2]:
  - id: 1
    data[2]{x,y}:
      10,20
      30,40
  - id: 2
    data[1]{x,y}:
      50,60"""
        result = decode(text)
        assert result == [
            {"id": 1, "data": [{"x": 10, "y": 20}, {"x": 30, "y": 40}]},
            {"id": 2, "data": [{"x": 50, "y": 60}]},
        ]
