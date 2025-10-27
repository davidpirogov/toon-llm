"""
Comprehensive test suite for the TOON LLM CLI using Typer's CliRunner.

Tests cover all code paths including:
- Encode command with various options
- Decode command with various options
- File I/O (reading from files, writing to files)
- stdin/stdout handling
- Error handling (verbose and non-verbose)
- Version flag
- Help text
- All CLI options (indent, delimiter, length_marker, pretty, validate)
"""

import json

import pytest
from typer.testing import CliRunner

from toon import __version__
from toon.main import app

# Create a CliRunner instance
runner = CliRunner()


class TestCLIVersion:
    """Test version and help functionality."""

    def test_version_flag(self):
        """Test --version flag displays version."""
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert f"pytoon {__version__}" in result.stdout

    def test_version_short_flag(self):
        """Test -v short flag displays version."""
        result = runner.invoke(app, ["-v"])
        assert result.exit_code == 0
        assert f"pytoon {__version__}" in result.stdout

    def test_help_flag(self):
        """Test --help flag displays help."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "TOON LLM: Token-Oriented Object Notation for LLMs" in result.stdout
        assert "encode" in result.stdout
        assert "decode" in result.stdout

    def test_encode_help(self):
        """Test encode command help."""
        result = runner.invoke(app, ["encode", "--help"])
        assert result.exit_code == 0
        assert "Encode JSON data to TOON format" in result.stdout
        assert "--indent" in result.stdout
        assert "--delimiter" in result.stdout
        assert "--length-marker" in result.stdout

    def test_decode_help(self):
        """Test decode command help."""
        result = runner.invoke(app, ["decode", "--help"])
        assert result.exit_code == 0
        assert "Decode TOON format to JSON" in result.stdout
        assert "--pretty" in result.stdout
        assert "--validate" in result.stdout


class TestCLIEncodeFromFile:
    """Test encoding from files."""

    def test_encode_simple_object_to_stdout(self, tmp_path):
        """Test encoding a simple object from file to stdout."""
        input_file = tmp_path / "input.json"
        input_file.write_text('{"name": "Alice", "age": 30}')

        result = runner.invoke(app, ["encode", str(input_file)])

        assert result.exit_code == 0
        assert "name: Alice" in result.stdout
        assert "age: 30" in result.stdout

    def test_encode_to_output_file(self, tmp_path):
        """Test encoding from file to output file."""
        input_file = tmp_path / "input.json"
        output_file = tmp_path / "output.toon"
        input_file.write_text('{"name": "Bob", "active": true}')

        result = runner.invoke(app, ["encode", str(input_file), "-o", str(output_file)])

        assert result.exit_code == 0
        assert output_file.exists()
        content = output_file.read_text()
        assert "name: Bob" in content
        assert "active: true" in content

    def test_encode_with_custom_indent(self, tmp_path):
        """Test encoding with custom indentation."""
        input_file = tmp_path / "input.json"
        input_file.write_text('{"user": {"name": "Charlie"}}')

        result = runner.invoke(app, ["encode", str(input_file), "--indent", "4"])

        assert result.exit_code == 0
        assert "user:" in result.stdout
        assert "    name: Charlie" in result.stdout  # 4 spaces

    def test_encode_with_custom_delimiter(self, tmp_path):
        """Test encoding with custom delimiter."""
        input_file = tmp_path / "input.json"
        input_file.write_text('{"items": [1, 2, 3]}')

        result = runner.invoke(app, ["encode", str(input_file), "--delimiter", "|"])

        assert result.exit_code == 0
        assert "items[3|]: 1|2|3" in result.stdout

    def test_encode_with_length_marker(self, tmp_path):
        """Test encoding with length marker."""
        input_file = tmp_path / "input.json"
        input_file.write_text('{"items": [1, 2, 3]}')

        result = runner.invoke(app, ["encode", str(input_file), "--length-marker"])

        assert result.exit_code == 0
        assert "items[#3]:" in result.stdout

    def test_encode_with_all_options(self, tmp_path):
        """Test encoding with all options combined."""
        input_file = tmp_path / "input.json"
        output_file = tmp_path / "output.toon"
        input_file.write_text('{"data": [10, 20, 30]}')

        result = runner.invoke(
            app,
            [
                "encode",
                str(input_file),
                "-o",
                str(output_file),
                "--indent",
                "4",
                "--delimiter",
                "\t",
                "--length-marker",
                "--verbose",
            ],
        )

        assert result.exit_code == 0
        assert output_file.exists()
        content = output_file.read_text()
        assert "data[#3\t]:" in content
        assert "Encoded to:" in result.stderr  # verbose message

    def test_encode_array_to_file(self, tmp_path):
        """Test encoding an array."""
        input_file = tmp_path / "input.json"
        input_file.write_text("[1, 2, 3, 4, 5]")

        result = runner.invoke(app, ["encode", str(input_file)])

        assert result.exit_code == 0
        assert "[5]:" in result.stdout

    def test_encode_nested_structure(self, tmp_path):
        """Test encoding nested structures."""
        input_file = tmp_path / "input.json"
        data = {
            "users": [
                {"name": "Alice", "age": 30},
                {"name": "Bob", "age": 25},
            ]
        }
        input_file.write_text(json.dumps(data))

        result = runner.invoke(app, ["encode", str(input_file)])

        assert result.exit_code == 0
        assert "users[2]{name,age}:" in result.stdout
        assert "Alice,30" in result.stdout
        assert "Bob,25" in result.stdout


class TestCLIEncodeFromStdin:
    """Test encoding from stdin."""

    def test_encode_from_stdin_explicit_dash(self):
        """Test encoding from stdin with explicit '-' argument."""
        result = runner.invoke(app, ["encode", "-"], input='{"name": "Alice"}')

        assert result.exit_code == 0
        assert "name: Alice" in result.stdout

    def test_encode_from_stdin_implicit(self):
        """Test encoding from stdin without any file argument."""
        result = runner.invoke(app, ["encode"], input='{"value": 42}')

        assert result.exit_code == 0
        assert "value: 42" in result.stdout

    def test_encode_from_stdin_to_file(self, tmp_path):
        """Test encoding from stdin to output file."""
        output_file = tmp_path / "output.toon"

        result = runner.invoke(
            app, ["encode", "-o", str(output_file)], input='{"test": true}'
        )

        assert result.exit_code == 0
        assert output_file.exists()
        assert "test: true" in output_file.read_text()

    def test_encode_from_stdin_with_delimiter(self):
        """Test encoding from stdin with custom delimiter."""
        result = runner.invoke(app, ["encode", "--delimiter", "|"], input="[1, 2, 3]")

        assert result.exit_code == 0
        assert "[3|]: 1|2|3" in result.stdout


class TestCLIDecodeFromFile:
    """Test decoding from files."""

    def test_decode_simple_object_to_stdout(self, tmp_path):
        """Test decoding a simple object from file to stdout."""
        input_file = tmp_path / "input.toon"
        input_file.write_text("name: Alice\nage: 30")

        result = runner.invoke(app, ["decode", str(input_file)])

        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data == {"name": "Alice", "age": 30}

    def test_decode_to_output_file(self, tmp_path):
        """Test decoding from file to output file."""
        input_file = tmp_path / "input.toon"
        output_file = tmp_path / "output.json"
        input_file.write_text("name: Bob\nactive: true")

        result = runner.invoke(app, ["decode", str(input_file), "-o", str(output_file)])

        assert result.exit_code == 0
        assert output_file.exists()
        data = json.loads(output_file.read_text())
        assert data == {"name": "Bob", "active": True}

    def test_decode_with_pretty_print(self, tmp_path):
        """Test decoding with pretty-printed JSON output."""
        input_file = tmp_path / "input.toon"
        input_file.write_text("user:\n  name: Charlie\n  age: 35")

        result = runner.invoke(app, ["decode", str(input_file), "--pretty"])

        assert result.exit_code == 0
        assert "{\n" in result.stdout  # Pretty-printed JSON
        assert '  "user"' in result.stdout

    def test_decode_with_custom_delimiter(self, tmp_path):
        """Test decoding with custom delimiter."""
        input_file = tmp_path / "input.toon"
        input_file.write_text("[3|]: 1|2|3")

        result = runner.invoke(app, ["decode", str(input_file), "--delimiter", "|"])

        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data == [1, 2, 3]

    def test_decode_with_validate_only(self, tmp_path):
        """Test decode with --validate flag."""
        input_file = tmp_path / "input.toon"
        input_file.write_text("name: Test\nvalue: 123")

        result = runner.invoke(app, ["decode", str(input_file), "--validate"])

        assert result.exit_code == 0
        assert "Valid" in result.stdout
        # Should not output JSON data
        assert "{" not in result.stdout

    def test_decode_validate_with_verbose(self, tmp_path):
        """Test decode with --validate and --verbose flags."""
        input_file = tmp_path / "input.toon"
        input_file.write_text("test: data")

        result = runner.invoke(
            app, ["decode", str(input_file), "--validate", "--verbose"]
        )

        assert result.exit_code == 0
        assert "✓ TOON LLM format is valid" in result.stderr

    def test_decode_array(self, tmp_path):
        """Test decoding an array."""
        input_file = tmp_path / "input.toon"
        input_file.write_text("[5]: 1,2,3,4,5")

        result = runner.invoke(app, ["decode", str(input_file)])

        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data == [1, 2, 3, 4, 5]

    def test_decode_tabular_data(self, tmp_path):
        """Test decoding tabular data."""
        input_file = tmp_path / "input.toon"
        input_file.write_text("[2]{name,age}:\nAlice,30\nBob,25")

        result = runner.invoke(app, ["decode", str(input_file), "--pretty"])

        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data == [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25},
        ]

    def test_decode_with_verbose_to_file(self, tmp_path):
        """Test decode with verbose flag writing to file."""
        input_file = tmp_path / "input.toon"
        output_file = tmp_path / "output.json"
        input_file.write_text("key: value")

        result = runner.invoke(
            app,
            [
                "decode",
                str(input_file),
                "-o",
                str(output_file),
                "--verbose",
            ],
        )

        assert result.exit_code == 0
        assert output_file.exists()
        assert "Decoded to:" in result.stderr


class TestCLIDecodeFromStdin:
    """Test decoding from stdin."""

    def test_decode_from_stdin_explicit_dash(self):
        """Test decoding from stdin with explicit '-' argument."""
        result = runner.invoke(app, ["decode", "-"], input="name: Alice")

        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data == {"name": "Alice"}

    def test_decode_from_stdin_implicit(self):
        """Test decoding from stdin without any file argument."""
        result = runner.invoke(app, ["decode"], input="value: 42")

        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data == {"value": 42}

    def test_decode_from_stdin_to_file(self, tmp_path):
        """Test decoding from stdin to output file."""
        output_file = tmp_path / "output.json"

        result = runner.invoke(
            app, ["decode", "-o", str(output_file)], input="test: true"
        )

        assert result.exit_code == 0
        assert output_file.exists()
        data = json.loads(output_file.read_text())
        assert data == {"test": True}

    def test_decode_from_stdin_with_pretty(self):
        """Test decoding from stdin with pretty print."""
        result = runner.invoke(app, ["decode", "--pretty"], input="[3]: a,b,c")

        assert result.exit_code == 0
        assert "[\n" in result.stdout  # Pretty-printed
        data = json.loads(result.stdout)
        assert data == ["a", "b", "c"]


class TestCLIErrorHandling:
    """Test error handling in CLI."""

    def test_encode_file_not_found(self):
        """Test encoding with non-existent input file."""
        result = runner.invoke(app, ["encode", "nonexistent.json"])

        assert result.exit_code == 1
        assert "Error: Input file" in result.stderr
        assert "not found" in result.stderr

    def test_encode_invalid_json(self, tmp_path):
        """Test encoding with invalid JSON input."""
        input_file = tmp_path / "invalid.json"
        input_file.write_text("{invalid json")

        result = runner.invoke(app, ["encode", str(input_file)])

        assert result.exit_code == 1
        assert "Error: Invalid JSON input" in result.stderr

    def test_encode_invalid_json_with_verbose(self, tmp_path):
        """Test encoding with invalid JSON and verbose flag."""
        input_file = tmp_path / "invalid.json"
        input_file.write_text("not json at all")

        result = runner.invoke(app, ["encode", str(input_file), "--verbose"])

        assert result.exit_code == 1
        assert "Error: Invalid JSON input" in result.stderr
        assert "Traceback" in result.stderr  # Stack trace with verbose

    def test_encode_invalid_json_from_stdin(self):
        """Test encoding invalid JSON from stdin."""
        result = runner.invoke(app, ["encode"], input="{not valid")

        assert result.exit_code == 1
        assert "Error: Invalid JSON input" in result.stderr

    def test_decode_file_not_found(self):
        """Test decoding with non-existent input file."""
        result = runner.invoke(app, ["decode", "nonexistent.toon"])

        assert result.exit_code == 1
        assert "Error: Input file" in result.stderr
        assert "not found" in result.stderr

    def test_decode_invalid_toon_format(self, tmp_path):
        """Test decoding with invalid TOON format."""
        input_file = tmp_path / "invalid.toon"
        input_file.write_text("[broken format")

        result = runner.invoke(app, ["decode", str(input_file)])

        assert result.exit_code == 1
        assert "Error: Decoding failed" in result.stderr

    def test_decode_invalid_toon_with_verbose(self, tmp_path):
        """Test decoding invalid TOON format with verbose flag."""
        input_file = tmp_path / "invalid.toon"
        input_file.write_text("[999]: a,b,c")  # Length mismatch

        result = runner.invoke(app, ["decode", str(input_file), "--verbose"])

        assert result.exit_code == 1
        assert "Error: Decoding failed" in result.stderr
        assert "Traceback" in result.stderr  # Stack trace with verbose

    def test_decode_invalid_from_stdin(self):
        """Test decoding invalid TOON from stdin."""
        result = runner.invoke(app, ["decode"], input="[malformed")

        assert result.exit_code == 1
        assert "Error: Decoding failed" in result.stderr

    def test_encode_invalid_indent_value(self, tmp_path):
        """Test encoding with invalid indent value (should be caught by typer)."""
        input_file = tmp_path / "input.json"
        input_file.write_text('{"test": true}')

        result = runner.invoke(app, ["encode", str(input_file), "--indent", "0"])

        # Typer validates min=1, so this should fail
        assert result.exit_code != 0


class TestCLIRoundTrip:
    """Test round-trip encoding and decoding."""

    def test_roundtrip_simple_object(self, tmp_path):
        """Test encoding then decoding a simple object."""
        input_file = tmp_path / "input.json"
        toon_file = tmp_path / "encoded.toon"
        output_file = tmp_path / "output.json"

        original_data = {"name": "Alice", "age": 30, "active": True}
        input_file.write_text(json.dumps(original_data))

        # Encode
        result = runner.invoke(app, ["encode", str(input_file), "-o", str(toon_file)])
        assert result.exit_code == 0

        # Decode
        result = runner.invoke(app, ["decode", str(toon_file), "-o", str(output_file)])
        assert result.exit_code == 0

        # Compare
        decoded_data = json.loads(output_file.read_text())
        assert decoded_data == original_data

    def test_roundtrip_with_custom_delimiter(self, tmp_path):
        """Test round-trip with custom delimiter."""
        input_file = tmp_path / "input.json"
        toon_file = tmp_path / "encoded.toon"

        original_data = {"items": [1, 2, 3, 4, 5]}
        input_file.write_text(json.dumps(original_data))

        # Encode with pipe delimiter
        runner.invoke(
            app,
            [
                "encode",
                str(input_file),
                "-o",
                str(toon_file),
                "--delimiter",
                "|",
            ],
        )

        # Decode with pipe delimiter
        result = runner.invoke(app, ["decode", str(toon_file), "--delimiter", "|"])

        assert result.exit_code == 0
        decoded_data = json.loads(result.stdout)
        assert decoded_data == original_data

    def test_roundtrip_nested_structure(self):
        """Test round-trip with nested structure."""
        original_data = {
            "users": [
                {"name": "Alice", "age": 30},
                {"name": "Bob", "age": 25},
            ],
            "metadata": {"version": 1, "count": 2},
        }

        # Encode to stdout, then decode from stdin
        encode_result = runner.invoke(app, ["encode"], input=json.dumps(original_data))
        assert encode_result.exit_code == 0

        decode_result = runner.invoke(app, ["decode"], input=encode_result.stdout)
        assert decode_result.exit_code == 0

        decoded_data = json.loads(decode_result.stdout)
        assert decoded_data == original_data

    def test_roundtrip_with_length_marker(self, tmp_path):
        """Test round-trip with length marker enabled."""
        input_file = tmp_path / "input.json"
        original_data = [10, 20, 30, 40, 50]
        input_file.write_text(json.dumps(original_data))

        # Encode with length marker
        encode_result = runner.invoke(
            app, ["encode", str(input_file), "--length-marker"]
        )
        assert encode_result.exit_code == 0
        assert "[#5]:" in encode_result.stdout

        # Decode
        decode_result = runner.invoke(app, ["decode"], input=encode_result.stdout)
        assert decode_result.exit_code == 0

        decoded_data = json.loads(decode_result.stdout)
        assert decoded_data == original_data


class TestCLIEdgeCases:
    """Test edge cases and special scenarios."""

    def test_encode_empty_object(self, tmp_path):
        """Test encoding an empty object."""
        input_file = tmp_path / "input.json"
        input_file.write_text("{}")

        result = runner.invoke(app, ["encode", str(input_file)])

        assert result.exit_code == 0

    def test_encode_empty_array(self, tmp_path):
        """Test encoding an empty array."""
        input_file = tmp_path / "input.json"
        input_file.write_text("[]")

        result = runner.invoke(app, ["encode", str(input_file)])

        assert result.exit_code == 0

    def test_encode_null_value(self, tmp_path):
        """Test encoding null value."""
        input_file = tmp_path / "input.json"
        input_file.write_text("null")

        result = runner.invoke(app, ["encode", str(input_file)])

        assert result.exit_code == 0
        assert "null" in result.stdout

    def test_encode_string_value(self, tmp_path):
        """Test encoding a single string."""
        input_file = tmp_path / "input.json"
        input_file.write_text('"hello world"')

        result = runner.invoke(app, ["encode", str(input_file)])

        assert result.exit_code == 0

    def test_encode_number_value(self, tmp_path):
        """Test encoding a single number."""
        input_file = tmp_path / "input.json"
        input_file.write_text("42")

        result = runner.invoke(app, ["encode", str(input_file)])

        assert result.exit_code == 0
        assert "42" in result.stdout

    def test_encode_boolean_true(self, tmp_path):
        """Test encoding boolean true."""
        input_file = tmp_path / "input.json"
        input_file.write_text("true")

        result = runner.invoke(app, ["encode", str(input_file)])

        assert result.exit_code == 0
        assert "true" in result.stdout

    def test_encode_unicode_characters(self, tmp_path):
        """Test encoding Unicode characters."""
        input_file = tmp_path / "input.json"
        input_file.write_text('{"emoji": "😀", "chinese": "你好"}')

        result = runner.invoke(app, ["encode", str(input_file)])

        assert result.exit_code == 0
        assert "😀" in result.stdout
        assert "你好" in result.stdout

    def test_decode_unicode_characters(self, tmp_path):
        """Test decoding Unicode characters."""
        input_file = tmp_path / "input.toon"
        input_file.write_text("emoji: 😀\ntext: 你好")

        result = runner.invoke(app, ["decode", str(input_file)])

        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["emoji"] == "😀"
        assert data["text"] == "你好"

    def test_encode_large_numbers(self, tmp_path):
        """Test encoding large numbers."""
        input_file = tmp_path / "input.json"
        input_file.write_text('{"big": 9007199254740991}')  # Max safe integer in JS

        result = runner.invoke(app, ["encode", str(input_file)])

        assert result.exit_code == 0

    def test_encode_special_string_characters(self, tmp_path):
        """Test encoding strings with special characters."""
        input_file = tmp_path / "input.json"
        data = {"text": 'line1\nline2\ttab\r\nwindows"quote"'}
        input_file.write_text(json.dumps(data))

        result = runner.invoke(app, ["encode", str(input_file)])

        assert result.exit_code == 0

    def test_validate_valid_format(self, tmp_path):
        """Test validate flag with valid TOON format."""
        input_file = tmp_path / "input.toon"
        input_file.write_text("key1: value1\nkey2: value2")

        result = runner.invoke(app, ["decode", str(input_file), "--validate"])

        assert result.exit_code == 0
        assert "Valid" in result.stdout

    def test_validate_invalid_format(self, tmp_path):
        """Test validate flag with invalid TOON format."""
        input_file = tmp_path / "input.toon"
        input_file.write_text("[broken")

        result = runner.invoke(app, ["decode", str(input_file), "--validate"])

        assert result.exit_code == 1
        assert "Error: Decoding failed" in result.stderr


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
