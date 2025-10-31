# TOON LLM Python Implementation Guide

Complete API reference and usage guide for the TOON LLM Python library.

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Encoder API](#encoder-api)
- [Decoder API](#decoder-api)
- [Type System](#type-system)
- [Configuration](#configuration)
- [Error Handling](#error-handling)
- [Python-Specific Features](#python-specific-features)
- [Advanced Usage](#advanced-usage)
- [Performance Considerations](#performance-considerations)

---

## Installation

### Using uv (Recommended)

```bash
# Add to existing project
uv add toon-llm

# Or install in current environment
uv pip install toon-llm
```

### Using pip

```bash
pip install toon-llm
```

---

## Quick Start

### Basic Encoding

```python
from toon import encode

# Primitives
encode(None)           # → 'null'
encode(True)           # → 'true'
encode(42)             # → '42'
encode(3.14)           # → '3.14'
encode("hello")        # → 'hello'

# Objects (dictionaries)
encode({"name": "Alice", "age": 30})
# → 'name: Alice\nage: 30'

# Arrays (lists)
encode([1, 2, 3])
# → '[3]: 1,2,3'
```

### Basic Decoding

```python
from toon import decode

# Primitives
decode('null')         # → None
decode('true')         # → True
decode('42')           # → 42
decode('3.14')         # → 3.14
decode('hello')        # → 'hello'

# Objects
decode('name: Alice\nage: 30')
# → {'name': 'Alice', 'age': 30}

# Arrays
decode('[3]: 1,2,3')
# → [1, 2, 3]
```

### Round-Trip Serialization

```python
from toon import encode, decode

data = {
    "users": [
        {"name": "Alice", "score": 100},
        {"name": "Bob", "score": 95}
    ]
}

# Encode to TOON LLM format
encoded = encode(data)
print(encoded)
# users[2]:
#   name,score
#   Alice,100
#   Bob,95

# Decode back to Python
decoded = decode(encoded)
assert decoded == data
```

---

## Encoder API

### `encode()`

Main function to encode Python values to TOON LLM format.

```python
def encode(
    value: Any,
    options: EncodeOptions | None = None,
    *,
    indent: int = 2,
    delimiter: str = ",",
    length_marker: Literal["#"] | Literal[False] = False,
) -> str:
    """
    Encode a Python value to TOON LLM format.

    Args:
        value: The value to encode (any JSON-serializable type)
        options: Pre-configured EncodeOptions (overrides keyword args)
        indent: Number of spaces per indentation level (default: 2)
        delimiter: Delimiter for arrays: ',', '\t', or '|' (default: ',')
        length_marker: Use '#' prefix in array headers or False (default: False)

    Returns:
        TOON LLM formatted string

    Raises:
        EncodeError: If encoding fails
        ValidationError: If options are invalid (from Pydantic)
    """
```

#### Examples

**Simple Values:**

```python
from toon import encode

# String quoting is automatic
encode("hello world")           # → '"hello world"'  (has spaces)
encode("simple")                # → 'simple'         (safe unquoted)
encode("")                      # → '""'             (empty)
encode("true")                  # → '"true"'         (ambiguous)

# Numbers
encode(0)                       # → '0'
encode(-42)                     # → '-42'
encode(3.14159)                 # → '3.14159'
encode(2.0)                     # → '2'              (whole number -> int)
encode(1e6)                     # → '1000000'        (whole number -> int)
encode(1e-10)                   # → '1e-10'          (scientific notation)

# Float encoding matches json.dumps() behavior
# Whole number floats become integers for compactness
# Other floats use Python's repr() which matches JSON defaults

# Booleans and null
encode(True)                    # → 'true'
encode(False)                   # → 'false'
encode(None)                    # → 'null'
```

**Objects (Dictionaries):**

```python
# Simple object
encode({"name": "Alice", "age": 30})
# name: Alice
# age: 30

# Nested objects
encode({
    "user": {
        "name": "Bob",
        "role": "admin"
    }
})
# user:
#   name: Bob
#   role: admin

# Keys are automatically quoted when needed
encode({"first name": "Alice", "": "empty key"})
# "first name": Alice
# "": empty key
```

**Arrays (Lists):**

```python
# Inline format (primitives only)
encode([1, 2, 3])
# [3]: 1,2,3

# Tabular format (uniform objects)
encode([
    {"name": "Alice", "age": 30},
    {"name": "Bob", "age": 25}
])
# [2]:
#   name,age
#   Alice,30
#   Bob,25

# List format (mixed types or nested structures)
encode([
    {"id": 1, "type": "user"},
    {"id": 2, "type": "admin", "level": 5}
])
# [2]:
#   - id: 1
#     type: user
#   - id: 2
#     type: admin
#     level: 5
```

**Custom Options:**

```python
# Custom delimiter
encode([1, 2, 3], delimiter="|")
# [3|]: 1|2|3

# Length marker
encode([1, 2, 3], length_marker="#")
# [#3]: 1,2,3

# Custom indentation
encode({"a": {"b": 1}}, indent=4)
# a:
#     b: 1

# Combined options
from toon import EncodeOptions

options = EncodeOptions(
    indent=4,
    delimiter="\t",
    length_marker="#"
)
encode([1, 2, 3], options=options)
# [#3	]: 1	2	3
```

---

## Decoder API

### `decode()`

Main function to decode TOON LLM format strings to Python values.

```python
def decode(
    text: str,
    options: DecodeOptions | None = None,
    *,
    delimiter: str = ",",
) -> JsonValue:
    """
    Decode a TOON LLM formatted string to Python value.

    Args:
        text: The TOON LLM formatted string to decode
        options: Pre-configured DecodeOptions (overrides keyword args)
        delimiter: Expected delimiter in arrays: ',', '\t', or '|' (default: ',')

    Returns:
        Decoded Python value (dict, list, or primitive)

    Raises:
        DecodeError: If decoding fails or format is invalid
        ValidationError: If options are invalid (from Pydantic)
    """
```

#### Examples

**Simple Values:**

```python
from toon import decode

# Primitives
decode('null')                  # → None
decode('true')                  # → True
decode('false')                 # → False
decode('42')                    # → 42
decode('3.14')                  # → 3.14
decode('hello')                 # → 'hello'

# Quoted strings
decode('"hello world"')         # → 'hello world'
decode('""')                    # → ''
decode('"true"')                # → 'true' (string, not boolean)
```

**Objects:**

```python
# Simple object
decode('name: Alice\nage: 30')
# → {'name': 'Alice', 'age': 30}

# Nested object
decode('''
user:
  name: Bob
  role: admin
'''.strip())
# → {'user': {'name': 'Bob', 'role': 'admin'}}

# Quoted keys
decode('"first name": Alice')
# → {'first name': 'Alice'}
```

**Arrays:**

```python
# Inline format
decode('[3]: 1,2,3')
# → [1, 2, 3]

# Tabular format
decode('''
[2]:
  name,age
  Alice,30
  Bob,25
'''.strip())
# → [{'name': 'Alice', 'age': 30}, {'name': 'Bob', 'age': 25}]

# List format
decode('''
[2]:
  - id: 1
    type: user
  - id: 2
    type: admin
'''.strip())
# → [{'id': 1, 'type': 'user'}, {'id': 2, 'type': 'admin'}]
```

**Custom Options:**

```python
from toon import DecodeOptions

# Custom delimiter
decode('[3|]: 1|2|3', delimiter='|')
# → [1, 2, 3]

# Using options object
options = DecodeOptions(delimiter='\t')
decode('[3\t]: 1\t2\t3', options=options)
# → [1, 2, 3]
```

---

## Type System

TOON LLM uses a well-defined type system based on JSON types.

### Type Aliases

```python
from toon import JsonPrimitive, JsonArray, JsonObject, JsonValue

# Primitive types
JsonPrimitive = str | int | float | bool | None

# Array type
JsonArray = list[JsonValue]

# Object type
JsonObject = dict[str, JsonValue]

# Any JSON value
JsonValue = JsonPrimitive | JsonArray | JsonObject
```

### Type Guards

TOON LLM provides type guards for runtime type checking:

```python
from toon.normalize import (
    is_json_primitive,
    is_json_array,
    is_json_object,
    is_array_of_primitives,
    is_array_of_arrays,
    is_array_of_objects,
)

# Check types
value = [1, 2, 3]
assert is_json_array(value)
assert is_array_of_primitives(value)

# Used by encoder to choose array format
data = [{"a": 1}, {"a": 2}]
if is_array_of_objects(data):
    # Will use tabular format
    pass
```

---

## Configuration

### `EncodeOptions`

Pydantic model for encoding configuration.

```python
from toon import EncodeOptions

class EncodeOptions(BaseModel):
    """Configuration options for encoding."""

    indent: int = 2
    """Number of spaces per indentation level (must be >= 0)"""

    delimiter: str = ","
    """Delimiter for arrays: ',', '\t', or '|'"""

    length_marker: Literal["#"] | Literal[False] = False
    """Use '#' prefix in array headers, or False to disable"""
```

#### Examples

```python
# Default options
options = EncodeOptions()
assert options.indent == 2
assert options.delimiter == ","
assert options.length_marker is False

# Custom options
options = EncodeOptions(
    indent=4,
    delimiter="\t",
    length_marker="#"
)

# Options are immutable (frozen)
try:
    options.indent = 8
except ValidationError:
    print("Cannot modify frozen options")

# Options are validated
try:
    EncodeOptions(indent=-1)
except ValidationError:
    print("indent must be >= 0")

# Extra fields are rejected
try:
    EncodeOptions(unknown_field=True)
except ValidationError:
    print("Extra fields not allowed")
```

### `DecodeOptions`

Pydantic model for decoding configuration.

```python
from toon import DecodeOptions

class DecodeOptions(BaseModel):
    """Configuration options for decoding."""

    delimiter: str = ","
    """Expected delimiter in arrays: ',', '\t', or '|'"""
```

#### Examples

```python
# Default options
options = DecodeOptions()
assert options.delimiter == ","

# Custom delimiter
options = DecodeOptions(delimiter="\t")

# Options are immutable and validated
try:
    options.delimiter = "|"
except ValidationError:
    print("Cannot modify frozen options")
```

### `Delimiters` Enum

Convenient enum for common delimiters.

```python
from toon import Delimiters

# Available delimiters
Delimiters.comma     # → ","
Delimiters.tab       # → "\t"
Delimiters.pipe      # → "|"

# Usage
from toon import encode, Delimiters

encode([1, 2, 3], delimiter=Delimiters.pipe)
# [3|]: 1|2|3
```

---

## Error Handling

### `EncodeError`

Raised when encoding fails.

```python
from toon import encode, EncodeError

try:
    # This will work - non-serializable values become None
    result = encode(object())
    assert result == "null"
except EncodeError as e:
    print(f"Encoding failed: {e}")
```

### `DecodeError`

Raised when decoding fails or format is invalid.

```python
from toon import decode, DecodeError

try:
    # Invalid array length
    decode('[3]: 1,2')  # Says 3 items, but only has 2
except DecodeError as e:
    print(f"Decoding failed: {e}")

try:
    # Invalid format
    decode('invalid: [not a real format]')
except DecodeError as e:
    print(f"Decoding failed: {e}")
```

### Validation Errors

Pydantic validation errors for invalid options.

```python
from pydantic import ValidationError
from toon import EncodeOptions

try:
    EncodeOptions(indent=-1)
except ValidationError as e:
    print(e.errors())
    # [{'type': 'greater_than_equal', 'loc': ('indent',), ...}]
```

---

## Python-Specific Features

TOON LLM automatically normalizes Python-specific types during encoding.

### Datetime Objects

```python
from datetime import datetime
from toon import encode

now = datetime(2024, 1, 15, 10, 30, 0)
encode(now)
# → '"2024-01-15T10:30:00"'

# With timezone
from datetime import timezone
now_utc = datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
encode(now_utc)
# → '"2024-01-15T10:30:00+00:00"'
```

### Dataclasses

```python
from dataclasses import dataclass
from toon import encode

@dataclass
class User:
    name: str
    age: int

user = User(name="Alice", age=30)
encode(user)
# name: Alice
# age: 30
```

### Pydantic Models

```python
from pydantic import BaseModel
from toon import encode

class User(BaseModel):
    name: str
    age: int
    active: bool = True

user = User(name="Bob", age=25)
encode(user)
# name: Bob
# age: 25
# active: true
```

### Sets

Sets are converted to lists (order may vary).

```python
from toon import encode

data = {"tags": {1, 2, 3}}
encode(data)
# tags[3]: 1,2,3  (order may differ)
```

### Tuples

Tuples are treated as lists.

```python
from toon import encode

encode((1, 2, 3))
# [3]: 1,2,3
```

### Special Numbers

```python
from toon import encode

# Negative zero is canonicalized
encode(-0.0)
# → '0'

# Infinity and NaN become null
encode(float('inf'))    # → 'null'
encode(float('nan'))    # → 'null'
```

### Non-Serializable Values

Non-serializable objects are automatically converted to `None`.

```python
from toon import encode

class CustomClass:
    pass

obj = CustomClass()
encode(obj)
# → 'null'

# In collections
encode({"obj": obj})
# obj: null
```

---

## Advanced Usage

### Nested Structures

```python
from toon import encode

data = {
    "company": "TechCorp",
    "employees": [
        {
            "name": "Alice",
            "role": "Engineer",
            "projects": ["API", "Database"]
        },
        {
            "name": "Bob",
            "role": "Designer",
            "projects": ["UI", "UX"]
        }
    ]
}

result = encode(data)
print(result)
# company: TechCorp
# employees[2]:
#   - name: Alice
#     role: Engineer
#     projects[2]: API,Database
#   - name: Bob
#     role: Designer
#     projects[2]: UI,UX
```

### Custom Normalization

For more control over serialization, normalize data before encoding:

```python
from toon import encode
from datetime import datetime

# Custom date formatting
data = {
    "timestamp": datetime.now(),
    "custom_data": SomeCustomClass()
}

# Pre-process before encoding
normalized = {
    "timestamp": data["timestamp"].strftime("%Y-%m-%d"),
    "custom_data": custom_serializer(data["custom_data"])
}

result = encode(normalized)
```

### Array Format Selection

TOON LLM automatically chooses the best array format:

```python
from toon import encode

# Inline format: all primitives
encode([1, 2, 3])
# [3]: 1,2,3

# Tabular format: uniform objects with same keys
encode([
    {"a": 1, "b": 2},
    {"a": 3, "b": 4}
])
# [2]:
#   a,b
#   1,2
#   3,4

# List format: different keys or nested structures
encode([
    {"a": 1},
    {"b": 2}
])
# [2]:
#   - a: 1
#   - b: 2
```

### Working with Files

```python
from toon import encode, decode
from pathlib import Path

# Save to file
data = {"config": {"debug": True, "port": 8080}}
Path("config.toon").write_text(encode(data))

# Load from file
loaded = decode(Path("config.toon").read_text())
assert loaded == data
```

### Pretty Printing

```python
from toon import encode

data = {"deeply": {"nested": {"data": [1, 2, 3]}}}

# Standard indent (2 spaces)
print(encode(data))
# deeply:
#   nested:
#     data[3]: 1,2,3

# Wide indent (4 spaces)
print(encode(data, indent=4))
# deeply:
#     nested:
#         data[3]: 1,2,3

# Minimal indent (1 space - minimal size)
print(encode(data, indent=1))
# deeply:
#  nested:
#   data[3]: 1,2,3
```

---

## Performance Considerations

### Encoding Performance

- **Primitives**: O(1) - Very fast
- **Objects**: O(n) where n is number of keys
- **Arrays**: O(n\*m) where n is length and m is average element complexity
- **Nested structures**: Recursive traversal

### Memory Usage

- Encoding builds output string progressively (efficient)
- Decoding parses entire input (requires full string in memory)
- Large arrays use appropriate format automatically

### Optimization Tips

1. **Use appropriate indentation**: Smaller indent = smaller output

```python
# Larger output
encode(data, indent=8)

# Smaller output
encode(data, indent=1)
```

2. **Choose delimiter wisely**: Tab is most compact

```python
# More characters
encode([1, 2, 3], delimiter=",")   # [3]: 1,2,3

# Fewer characters (single tab)
encode([1, 2, 3], delimiter="\t")  # [3	]: 1	2	3
```

3. **Pre-normalize complex objects**: If you have custom serialization logic

```python
# Slower: let TOON LLM normalize
encode(complex_object)

# Faster: pre-normalize
normalized = custom_normalize(complex_object)
encode(normalized)
```

---

## Best Practices

### 1. Use Type Hints

```python
from toon import encode, JsonObject

def save_config(config: JsonObject) -> str:
    """Save configuration to TOON LLM format."""
    return encode(config)
```

### 2. Handle Errors Gracefully

```python
from toon import decode, DecodeError

def load_config(text: str) -> dict:
    """Load configuration, return empty dict on error."""
    try:
        return decode(text)
    except DecodeError as e:
        logger.error(f"Failed to decode config: {e}")
        return {}
```

### 3. Use Options Objects for Consistency

```python
from toon import encode, EncodeOptions

# Define once, reuse everywhere
APP_ENCODE_OPTIONS = EncodeOptions(
    indent=2,
    delimiter=",",
    length_marker="#"
)

def save_data(data):
    return encode(data, options=APP_ENCODE_OPTIONS)
```

### 4. Validate Before Encoding

```python
from toon import encode
from pydantic import BaseModel

class Config(BaseModel):
    """Validated configuration."""
    host: str
    port: int
    debug: bool = False

# This validates before encoding
config = Config(host="localhost", port=8080)
encoded = encode(config)
```

### 5. Document Format Expectations

```python
def parse_user_data(text: str) -> dict:
    """
    Parse user data from TOON LLM format.

    Expected format:
        name: Alice
        age: 30
        tags[2]: python,coding

    Args:
        text: TOON LLM formatted user data

    Returns:
        Parsed user dictionary
    """
    from toon import decode
    return decode(text)
```

---

## See Also

- [Format Specification](../specification/README.md) - Complete TOON LLM format specification
- [Coding Standards](./CODING_STANDARDS.md) - For contributors
- [Build Instructions](./BUILD.md) - How to build and distribute the library
- [GitHub Repository](https://github.com/davidpirogov/toon-llm) - Source code and issues

---

## License

This implementation is part of the TOON LLM project. See the [LICENSE](../LICENSE) file for details.
