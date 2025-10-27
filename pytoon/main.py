"""
Command-line interface for PyToon encoding and decoding.

This module provides a CLI for encoding JSON to PyToon format and decoding
PyToon format back to JSON. It supports standard Unix behaviors like reading
from stdin and writing to stdout.
"""

import json
import sys
import traceback
from pathlib import Path
from typing import Annotated, Optional

import typer
from typing_extensions import Literal

from pytoon import __version__, decode, encode
from pytoon.errors import DecodeError, EncodeError

# Create the main Typer app
app = typer.Typer(
    name="pytoon",
    help="PyToon: Token-Oriented Object Notation for LLMs",
    add_completion=False,
)


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        typer.echo(f"pytoon {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        Optional[bool],
        typer.Option(
            "--version",
            "-v",
            callback=version_callback,
            is_eager=True,
            help="Show version and exit",
        ),
    ] = None,
) -> None:
    """
    PyToon CLI: Encode JSON to PyToon format or decode PyToon to JSON.

    Use 'pytoon encode' or 'pytoon decode' subcommands.
    """
    pass


@app.command(name="encode")
def encode_cmd(
    input_file: Annotated[
        Optional[Path],
        typer.Argument(
            help="Input JSON file (or '-' for stdin). If not specified, reads from stdin.",
            show_default=False,
        ),
    ] = None,
    output: Annotated[
        Optional[Path],
        typer.Option(
            "--output", "-o", help="Output file. If not specified, writes to stdout."
        ),
    ] = None,
    indent: Annotated[
        int,
        typer.Option(
            "--indent", "-i", help="Number of spaces per indentation level", min=1
        ),
    ] = 2,
    delimiter: Annotated[
        str,
        typer.Option("--delimiter", "-d", help="Delimiter for arrays and tables"),
    ] = ",",
    length_marker: Annotated[
        bool,
        typer.Option("--length-marker", "-l", help='Use "#" prefix for array lengths'),
    ] = False,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", help="Show verbose error messages with stack traces"),
    ] = False,
) -> None:
    """
    Encode JSON data to TOON format.

    Examples:
        pytoon encode input.json -o output.toon
        pytoon encode input.json
        cat input.json | pytoon encode
        pytoon encode - -o output.toon < input.json
        pytoon encode input.json --indent 4 --delimiter "|"
    """
    try:
        # Read input
        if input_file is None or str(input_file) == "-":
            # Read from stdin
            input_text = sys.stdin.read()
        else:
            # Read from file
            if not input_file.exists():
                typer.echo(f"Error: Input file '{input_file}' not found", err=True)
                raise typer.Exit(code=1)
            input_text = input_file.read_text(encoding="utf-8")

        # Parse JSON
        try:
            data = json.loads(input_text)
        except json.JSONDecodeError as e:
            typer.echo(f"Error: Invalid JSON input: {e}", err=True)
            if verbose:
                typer.echo(traceback.format_exc(), err=True)
            raise typer.Exit(code=1) from None

        # Encode to PyToon
        try:
            length_marker_value: Literal["#", False] = "#" if length_marker else False
            result = encode(
                data,
                indent=indent,
                delimiter=delimiter,
                length_marker=length_marker_value,
            )
        except (EncodeError, ValueError) as e:
            typer.echo(f"Error: Encoding failed: {e}", err=True)
            if verbose:
                typer.echo(traceback.format_exc(), err=True)
            raise typer.Exit(code=1) from None

        # Write output
        if output is None:
            # Write to stdout
            typer.echo(result)
        else:
            # Write to file
            output.write_text(result, encoding="utf-8")
            if verbose:
                typer.echo(f"Encoded to: {output}", err=True)

    except typer.Exit:
        raise
    except Exception as e:
        typer.echo(f"Error: Unexpected error: {e}", err=True)
        if verbose:
            typer.echo(traceback.format_exc(), err=True)
        raise typer.Exit(code=1) from None


@app.command(name="decode")
def decode_cmd(
    input_file: Annotated[
        Optional[Path],
        typer.Argument(
            help="Input PyToon file (or '-' for stdin). If not specified, reads from stdin.",
            show_default=False,
        ),
    ] = None,
    output: Annotated[
        Optional[Path],
        typer.Option(
            "--output", "-o", help="Output file. If not specified, writes to stdout."
        ),
    ] = None,
    delimiter: Annotated[
        str,
        typer.Option("--delimiter", "-d", help="Delimiter used in the PyToon format"),
    ] = ",",
    pretty: Annotated[
        bool,
        typer.Option(
            "--pretty", "-p", help="Pretty-print JSON output with indentation"
        ),
    ] = False,
    validate: Annotated[
        bool,
        typer.Option(
            "--validate", help="Only validate PyToon format without outputting"
        ),
    ] = False,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", help="Show verbose error messages with stack traces"),
    ] = False,
) -> None:
    """
    Decode TOON format to JSON.

    Examples:
        pytoon decode input.toon -o output.json
        pytoon decode input.toon --pretty
        cat input.toon | pytoon decode
        pytoon decode - -o output.json < input.toon
        pytoon decode input.toon --delimiter "|"
        pytoon decode input.toon --validate
    """
    try:
        # Read input
        if input_file is None or str(input_file) == "-":
            # Read from stdin
            input_text = sys.stdin.read()
        else:
            # Read from file
            if not input_file.exists():
                typer.echo(f"Error: Input file '{input_file}' not found", err=True)
                raise typer.Exit(code=1)
            input_text = input_file.read_text(encoding="utf-8")

        # Decode from PyToon
        try:
            result = decode(input_text, delimiter=delimiter)
        except DecodeError as e:
            typer.echo(f"Error: Decoding failed: {e}", err=True)
            if verbose:
                typer.echo(traceback.format_exc(), err=True)
            raise typer.Exit(code=1) from None

        # If validate-only mode, just report success
        if validate:
            if verbose:
                typer.echo("✓ PyToon format is valid", err=True)
            else:
                typer.echo("Valid")
            return

        # Convert to JSON
        if pretty:
            json_output = json.dumps(result, indent=2, ensure_ascii=False)
        else:
            json_output = json.dumps(result, ensure_ascii=False)

        # Write output
        if output is None:
            # Write to stdout
            typer.echo(json_output)
        else:
            # Write to file
            output.write_text(json_output, encoding="utf-8")
            if verbose:
                typer.echo(f"Decoded to: {output}", err=True)

    except typer.Exit:
        raise
    except Exception as e:
        typer.echo(f"Error: Unexpected error: {e}", err=True)
        if verbose:
            typer.echo(traceback.format_exc(), err=True)
        raise typer.Exit(code=1) from None


if __name__ == "__main__":
    app()
