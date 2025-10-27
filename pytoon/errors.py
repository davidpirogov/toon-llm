"""This module defines custom exceptions for the PyToon library."""


class EncodeError(ValueError):
    """Raised when TOON format encoding fails."""

    pass


class DecodeError(ValueError):
    """Raised when TOON format parsing fails."""

    pass
