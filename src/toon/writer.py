"""
Line writer utility for building multi-line output with proper indentation.

This module provides the LineWriter class for accumulating lines of text
with automatic indentation management.
"""

from toon.types import Depth


class LineWriter:
    """
    A writer for building multi-line output with proper indentation.

    The LineWriter accumulates lines of text, each with a specified depth level,
    and manages indentation automatically. Lines are joined with newlines when
    converted to a string.

    Attributes:
        indent: The indentation string (typically spaces)
        lines: Accumulated list of formatted lines

    Examples:
        >>> writer = LineWriter(indent="  ")
        >>> writer.push(0, "root")
        >>> writer.push(1, "child")
        >>> print(writer.to_string())
        root
          child
    """

    def __init__(self, indent: str = "  ") -> None:
        """
        Initialize a new LineWriter.

        Args:
            indent: The indentation string to use (default: two spaces)
        """
        self.indent = indent
        self.lines: list[str] = []

    def push(self, depth: Depth, content: str) -> None:
        """
        Add a line at the specified indentation depth.

        Args:
            depth: The indentation level (0 = no indent, 1 = one indent, etc.)
            content: The text content of the line
        """
        indentation = self.indent * depth
        self.lines.append(f"{indentation}{content}")

    def to_string(self) -> str:
        """
        Convert all accumulated lines to a single string.

        Returns:
            All lines joined with newline characters
        """
        return "\n".join(self.lines)

    def __str__(self) -> str:
        """String representation returns the formatted output."""
        return self.to_string()

    def __repr__(self) -> str:
        """Repr returns the formatted output for debugging."""
        return self.to_string()
