# PyToon Documentation

Welcome to the PyToon documentation. PyToon is a Python library for encoding and decoding Python data structures in a compact, human-readable text format.

## Documentation Files

### [IMPLEMENTATION.md](./IMPLEMENTATION.md) 📘

**Complete Python API reference and usage guide:**

- Installation instructions (pip and uv)
- Quick start guide with examples
- Encoder API documentation (`encode()` function)
- Decoder API documentation (`decode()` function)
- Type system and type aliases
- Configuration options (`EncodeOptions`, `DecodeOptions`)
- Error handling (`EncodeError`, `DecodeError`)
- Python-specific features (datetime, dataclasses, Pydantic models)
- Advanced usage patterns
- Performance considerations and best practices

### [LLM_PROMPTS.md](./LLM_PROMPTS.md) 🤖

**Guidance for Large Language Models:**

- Self-documenting format explanation (square brackets, curly braces)
- Lightweight prompt (<100 words) for quick LLM understanding
- Comprehensive prompt (<1000 words) for detailed LLM generation
- Format caveats and limitations
- Round-trip considerations
- Token optimization benefits
- Best practices for LLM interactions

### [CODING_STANDARDS.md](./CODING_STANDARDS.md) 🛠️

**Development standards for contributors:**

- Type annotation requirements
- Pydantic model usage
- Documentation standards
- Function design principles
- Error handling patterns
- Code organization guidelines
- Testing standards

## Quick Reference

### Installation

```bash
# Using uv (recommended)
uv add py-toon

# Using pip
pip install py-toon
```

### Basic Usage

```python
from pytoon import encode, decode

# Encode: Python → PyToon
data = {'name': 'Ada', 'age': 42}
encoded = encode(data)
print(encoded)
# name: Ada
# age: 42

# Decode: PyToon → Python
decoded = decode(encoded)
print(decoded)
# {'name': 'Ada', 'age': 42'}
```

### Common Examples

```python
# Simple values
encode(None)           # → 'null'
encode(True)           # → 'true'
encode(42)             # → '42'
encode("hello")        # → 'hello'

# Dictionaries
encode({'name': 'Alice', 'age': 30})
# → 'name: Alice\nage: 30'

# Lists (inline format)
encode([1, 2, 3])
# → '[3]: 1,2,3'

# Lists (tabular format for uniform objects)
encode([
    {'name': 'Alice', 'score': 100},
    {'name': 'Bob', 'score': 95}
])
# → '[2]:\n  name,score\n  Alice,100\n  Bob,95'

# Nested structures
encode({
    'user': {
        'id': 123,
        'tags': ['python', 'coding']
    }
})
# → 'user:\n  id: 123\n  tags[2]: python,coding'
```

### Configuration Options

```python
from pytoon import encode, EncodeOptions, Delimiters

# Custom delimiter
encode([1, 2, 3], delimiter='|')
# → '[3|]: 1|2|3'

# Using delimiter enum
encode([1, 2, 3], delimiter=Delimiters.tab)
# → '[3\t]: 1\t2\t3'

# Length marker
encode([1, 2, 3], length_marker='#')
# → '[#3]: 1,2,3'

# Custom indentation
encode({'a': {'b': 1}}, indent=4)
# → 'a:\n    b: 1'

# Using options object
options = EncodeOptions(
    indent=4,
    delimiter='|',
    length_marker='#'
)
encode([1, 2], options=options)
# → '[#2|]: 1|2'
```

### Python-Specific Features

PyToon automatically handles Python types:

```python
from datetime import datetime
from dataclasses import dataclass
from pydantic import BaseModel

# Datetime objects → ISO 8601 strings
encode(datetime(2024, 1, 15, 10, 30))
# → '"2024-01-15T10:30:00"'

# Dataclasses → dictionaries
@dataclass
class User:
    name: str
    age: int

encode(User("Alice", 30))
# → 'name: Alice\nage: 30'

# Pydantic models → dictionaries
class Config(BaseModel):
    host: str
    port: int

encode(Config(host="localhost", port=8080))
# → 'host: localhost\nport: 8080'

# Sets → lists
encode({1, 2, 3})
# → '[3]: 1,2,3'

# Tuples → lists
encode((1, 2, 3))
# → '[3]: 1,2,3'
```

## Additional Resources

### For Users

- **[IMPLEMENTATION.md](./IMPLEMENTATION.md)** - Complete API documentation and usage guide
- **[../specification/README.md](../specification/README.md)** - PyToon format specification
- **[../README.md](../README.md)** - Project overview and quick start

### For Contributors

- **[CODING_STANDARDS.md](./CODING_STANDARDS.md)** - Development standards and best practices
- **[../IMPLEMENTATION_PLAN.md](../IMPLEMENTATION_PLAN.md)** - Implementation roadmap
- **[../CHECKLIST.md](../CHECKLIST.md)** - Development progress tracking
- **[BUILD.md](./BUILD.md)** - Build and distribution instructions

## Support

- **Issues**: [GitHub Issues](https://github.com/davidpirogov/py-toon/issues)
- **Discussions**: [GitHub Discussions](https://github.com/davidpirogov/py-toon/discussions)

## License

This project is licensed under the terms specified in the [LICENSE](../LICENSE) file.
