# Coding Standards

This document defines the coding standards for the TOON LLM project, emphasizing Python 3.11 best practices and Pydantic for data validation.

## Table of Contents

1. [Type Annotations](#type-annotations)
2. [Pydantic Models](#pydantic-models)
3. [Documentation](#documentation)
4. [Function Design](#function-design)
5. [Error Handling](#error-handling)
6. [Code Organization](#code-organization)
7. [Formatting and Style](#formatting-and-style)
8. [Testing](#testing)

---

## Type Annotations

### Always Use Type Hints

**Required**: All functions must have type annotations for parameters and return values.

```python
# Good
def encode_primitive(value: JsonPrimitive, delimiter: str = COMMA) -> str:
    """Encode a primitive value."""
    return str(value)

# Bad
def encode_primitive(value, delimiter=COMMA):
    return str(value)
```

### Use Modern Type Syntax (Python 3.11)

**Required**: Use built-in generic types (PEP 585) instead of `typing` module equivalents.

```python
# Good - Python 3.11 style
def process_items(items: list[str]) -> dict[str, int]:
    """Process a list of items."""
    return {item: len(item) for item in items}

# Bad - Old style
from typing import List, Dict

def process_items(items: List[str]) -> Dict[str, int]:
    return {item: len(item) for item in items}
```

### Type Aliases

**Required**: Define type aliases for complex or reusable types at module level.

```python
# Good - Clear type aliases
JsonPrimitive = Union[str, int, float, bool, None]
JsonObject = dict[str, "JsonValue"]
JsonArray = list["JsonValue"]
JsonValue = Union[JsonPrimitive, JsonObject, JsonArray]
```

### Type Guards

**Preferred**: Use `TypeGuard` for runtime type checking functions.

```python
from typing import TypeGuard

def is_json_primitive(value: object) -> TypeGuard[JsonPrimitive]:
    """Check if value is a JSON primitive type."""
    return isinstance(value, (str, int, float, bool, type(None)))
```

### Literal Types

**Preferred**: Use `Literal` for fixed string/value options.

```python
from typing import Literal

Delimiter = Literal[",", "\t", "|"]
length_marker: Union[Literal["#"], Literal[False]] = False
```

---

## Pydantic Models

### Use Pydantic for Configuration

**Required**: Use Pydantic `BaseModel` for all configuration and data validation.

```python
from pydantic import BaseModel, Field, ConfigDict

class EncodeOptions(BaseModel):
    """Configuration options for encoding."""

    indent: int = Field(
        default=2,
        ge=0,
        description="Number of spaces per indentation level",
    )
    delimiter: str = Field(
        default=",",
        description="Delimiter for arrays",
    )

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        validate_default=True,
    )
```

### Field Definitions

**Required**: Always use `Field()` for fields with constraints or metadata.

```python
# Good - Explicit constraints
indent: int = Field(default=2, ge=0, description="Indentation spaces")

# Bad - No validation
indent: int = 2
```

### Model Configuration

**Required**: Configure models with these settings:

- `frozen=True`: Make models immutable after creation
- `extra="forbid"`: Reject unexpected fields
- `validate_default=True`: Validate default values

```python
model_config = ConfigDict(
    frozen=True,
    extra="forbid",
    validate_default=True,
)
```

### Factory Methods

**Preferred**: Use `@classmethod` for model creation from other types.

```python
@classmethod
def from_options(cls, options: EncodeOptions) -> "ResolvedEncodeOptions":
    """Create ResolvedEncodeOptions from EncodeOptions."""
    return cls(
        indent=" " * options.indent,
        delimiter=options.delimiter,
        length_marker=options.length_marker,
    )
```

---

## Documentation

### Module Docstrings

**Required**: Every module must have a docstring explaining its purpose.

```python
"""
Primitive value encoding and string handling utilities.

This module provides functions for encoding primitive values (strings, numbers,
booleans, null), handling string escaping and quoting, key encoding, and header
formatting for arrays and tables.
"""
```

### Function Docstrings

**Required**: All public functions must have complete docstrings with:

- One-line summary
- Detailed description (if needed)
- Args section
- Returns section
- Examples section (preferred)
- Raises section (if applicable)

```python
def encode_primitive(value: JsonPrimitive, delimiter: str = COMMA) -> str:
    """
    Encode a JSON primitive value to a string.

    Args:
        value: The primitive value (str, int, float, bool, or None)
        delimiter: The delimiter being used (affects string quoting)

    Returns:
        The encoded string representation

    Examples:
        >>> encode_primitive(None, ",")
        'null'
        >>> encode_primitive(True, ",")
        'true'
        >>> encode_primitive(42, ",")
        '42'
    """
    if value is None:
        return NULL_LITERAL
    # ...
```

### Class Docstrings

**Required**: Classes must document purpose, attributes, and provide usage examples.

```python
class LineWriter:
    """
    A writer for building multi-line output with proper indentation.

    The LineWriter accumulates lines of text, each with a specified depth level,
    and manages indentation automatically.

    Attributes:
        indent: The indentation string (typically spaces)
        lines: Accumulated list of formatted lines

    Examples:
        >>> writer = LineWriter(indent="  ")
        >>> writer.push(0, "root")
        >>> print(writer.to_string())
        root
    """
```

### Inline Comments

**Preferred**: Use inline comments for non-obvious logic, not for obvious code.

```python
# Good - Explains why
if isinstance(value, float) and value == 0 and str(value).startswith("-"):
    return 0  # Canonicalize -0 to 0

# Bad - States the obvious
x = x + 1  # Increment x
```

---

## Function Design

### Single Responsibility

**Required**: Functions should do one thing well. Keep functions focused and concise.

```python
# Good - Separate concerns
def encode_primitive(value: JsonPrimitive, delimiter: str) -> str:
    """Encode a primitive value."""
    # Only handles primitive encoding

def encode_object(value: JsonObject, writer: LineWriter, depth: Depth) -> None:
    """Encode an object."""
    # Only handles object encoding

# Bad - Does too much
def encode_everything(value: Any) -> str:
    # Handles primitives, objects, arrays, normalization, etc.
```

### Prefer Pure Functions

**Preferred**: Functions should avoid side effects when possible.

```python
# Good - Pure function
def escape_string(value: str) -> str:
    """Escape special characters."""
    return value.replace("\\", "\\\\").replace('"', '\\"')

# Acceptable - Explicit mutation via passed writer
def encode_object(value: JsonObject, writer: LineWriter, depth: Depth) -> None:
    """Encode object to writer."""
    for key, val in value.items():
        writer.push(depth, f"{key}: {val}")
```

### Parameter Ordering

**Required**: Order parameters logically:

1. Required positional parameters
2. Optional parameters with defaults
3. Keyword-only parameters (after `*`)

```python
# Good - Logical ordering
def encode_value(
    value: JsonValue,
    options: ResolvedEncodeOptions,
    *,
    depth: int = 0
) -> str:
    """Encode a value."""
    pass
```

### Default Arguments

**Warning**: Never use mutable defaults. Use `None` and initialize inside function.

```python
# Good
def process_items(items: list[str] | None = None) -> list[str]:
    """Process items."""
    if items is None:
        items = []
    return items

# Bad - Dangerous mutable default
def process_items(items: list[str] = []) -> list[str]:
    return items
```

---

## Error Handling

### Type Checking

**Required**: Validate types explicitly for public APIs.

```python
def _check_type(value: object, expected_types: Union[type, tuple], type_name: str) -> None:
    """Check that a value is an instance of expected types."""
    if not isinstance(value, expected_types):
        actual_type = type(value).__name__
        raise ValueError(f"Expected {type_name}, got {actual_type}")
```

### Use Specific Exceptions

**Required**: Raise specific exception types with clear messages.

```python
# Good - Specific and informative
if len(column_keys) == 0:
    raise ValueError("Cannot encode empty table: no columns available")

# Bad - Generic or unclear
if len(column_keys) == 0:
    raise Exception("Error")
```

### Input Validation

**Required**: Validate inputs at public API boundaries. Use Pydantic for configuration.

```python
class EncodeOptions(BaseModel):
    """Configuration with automatic validation."""
    indent: int = Field(default=2, ge=0)  # Validates indent >= 0
```

---

## Code Organization

### Module Structure

**Required**: Organize modules by functionality:

```
pytoon/
├── __init__.py          # Public API exports
├── types.py             # Type definitions and Pydantic models
├── constants.py         # Constants and enums
├── normalize.py         # Type normalization and guards
├── primitives.py        # Primitive value encoding
├── encoders.py          # Main encoding logic
└── writer.py            # Output utilities
```

### Import Organization

**Required**: Group imports in this order:

1. Standard library
2. Third-party packages
3. Local modules

```python
# Good - Organized imports
from dataclasses import asdict, is_dataclass
from datetime import datetime
from typing import Any, TypeGuard

from pydantic import BaseModel, Field

from toon.types import JsonValue
from toon.constants import COMMA
```

### Exports

**Required**: Define `__all__` in `__init__.py` to control public API.

```python
__all__ = [
    "encode",
    "EncodeOptions",
    "Delimiters",
    "JsonPrimitive",
    "JsonArray",
    "JsonObject",
    "JsonValue",
]
```

### Constants

**Required**: Define constants at module level using `Literal` or `Final`.

```python
from typing import Literal

# Good - Type-safe constants
NULL_LITERAL: Literal["null"] = "null"
TRUE_LITERAL: Literal["true"] = "true"
FALSE_LITERAL: Literal["false"] = "false"
```

### Enums

**Preferred**: Use `StrEnum` (Python 3.11+) for string constants.

```python
from enum import StrEnum

class Delimiters(StrEnum):
    comma = ","
    tab = "\t"
    pipe = "|"
```

---

## Formatting and Style

### Line Length

**Required**: Maximum line length is 110 characters (per `pyproject.toml`).

### Naming Conventions

**Required**:

- Functions and variables: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Type aliases: `PascalCase`
- Private functions/methods: `_leading_underscore`

```python
# Constants
NULL_LITERAL: Literal["null"] = "null"

# Type aliases
JsonPrimitive = Union[str, int, float, bool, None]

# Classes
class EncodeOptions(BaseModel):
    pass

# Functions
def encode_primitive(value: JsonPrimitive) -> str:
    pass

# Private functions
def _check_type(value: object, expected_types: type) -> None:
    pass
```

### String Quotes

**Required**: Use double quotes for strings that appear in output, single quotes for internal strings.

```python
# Good
DOUBLE_QUOTE: Literal['"'] = '"'
NULL_LITERAL: Literal["null"] = "null"
return f"{DOUBLE_QUOTE}{escaped}{DOUBLE_QUOTE}"

# Flexible - Either is fine for regular strings
message = "Processing items"
message = 'Processing items'
```

### F-strings

**Preferred**: Use f-strings for string formatting.

```python
# Good
return f"{key}: {value}"
raise ValueError(f"Expected {type_name}, got {actual_type}")

# Bad
return "{}: {}".format(key, value)
return "%s: %s" % (key, value)
```

---

## Testing

### Test Organization

**Required**: Organize tests in classes by functionality.

```python
class TestPrimitives:
    """Test encoding of primitive values."""

    def test_none(self):
        assert encode(None) == "null"

    def test_bool_true(self):
        assert encode(True) == "true"


class TestObjects:
    """Test encoding of objects."""

    def test_simple_object(self):
        result = encode({"name": "Alice"})
        assert result == "name: Alice"
```

### Test Naming

**Required**: Test function names should clearly describe what they test.

```python
# Good - Descriptive names
def test_empty_string(self):
    assert encode("") == '""'

def test_string_with_spaces(self):
    assert encode("hello world") == '"hello world"'

# Bad - Unclear names
def test_case1(self):
    assert encode("") == '""'
```

### Assertions

**Required**: Use clear, direct assertions. One logical assertion per test.

```python
# Good
def test_simple_object(self):
    result = encode({"name": "Alice", "age": 30})
    assert result == "name: Alice\nage: 30"

# Bad - Multiple unrelated assertions
def test_everything(self):
    assert encode(None) == "null"
    assert encode(True) == "true"
    assert encode({"x": 1}) == "x: 1"
```

### Fixtures

**Preferred**: Use pytest fixtures for shared test data.

```python
@pytest.fixture
def sample_config():
    """Provide a sample configuration for tests."""
    return EncodeOptions(indent=4, delimiter="|")


def test_with_config(sample_config):
    result = encode_with_options(data, sample_config)
    assert result == expected
```

---

## Summary

This document establishes the coding standards for TOON LLM. Key principles:

1. **Type Safety**: Use Python 3.11 type hints everywhere
2. **Validation**: Use Pydantic for configuration and data validation
3. **Documentation**: Comprehensive docstrings with examples
4. **Simplicity**: Single-responsibility functions, pure when possible
5. **Clarity**: Clear naming, explicit over implicit
6. **Testing**: Organized tests with descriptive names

When in doubt, refer to the existing codebase as examples of these standards in practice.
