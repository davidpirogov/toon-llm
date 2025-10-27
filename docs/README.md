# PyToon Documentation

Welcome to the PyToon documentation. PyToon is a Python library for encoding Python data structures into a compact, human-readable text format.

## Documentation Files

### [SPECIFICATION.md](./SPECIFICATION.md)
Complete specification of the PyToon encoding format, including:
- Encoding rules for all primitive types (strings, numbers, booleans, null)
- Dictionary (object) encoding with key/value quoting rules
- List (array) encoding with multiple formats (inline, tabular, list)
- Complex nested structure handling
- Configuration options (delimiter, length marker)
- Non-serializable value handling
- Python-specific implementation notes
- Full API design with type hints
- Comprehensive test requirements

## Quick Reference

### Basic Usage

```python
from pytoon import encode

# Simple values
encode('hello')  # → 'hello'
encode(42)       # → '42'
encode(True)     # → 'true'

# Dictionaries
encode({'name': 'Ada', 'age': 42})
# → 'name: Ada\nage: 42'

# Lists
encode(['a', 'b', 'c'])
# → '[3]: a,b,c'

# Nested structures
encode({
    'user': {
        'id': 123,
        'tags': ['reading', 'gaming']
    }
})
# → 'user:\n  id: 123\n  tags[2]: reading,gaming'
```

### Configuration Options

```python
# Custom delimiter
encode(['a', 'b', 'c'], delimiter='|')
# → '[3|]: a|b|c'

# Length marker
encode([1, 2, 3], length_marker='#')
# → '[#3]: 1,2,3'

# Combined
encode(['x', 'y'], delimiter='|', length_marker='#')
# → '[#2|]: x|y'
```

## Implementation Status

- [ ] Core encoding logic
- [ ] Primitive type handling
- [ ] Dictionary encoding
- [ ] List encoding (inline format)
- [ ] List encoding (tabular format)
- [ ] List encoding (list format)
- [ ] Delimiter option support
- [ ] Length marker option support
- [ ] Non-serializable value handling
- [ ] Test suite
- [ ] Documentation
- [ ] Examples

## Development

See [SPECIFICATION.md](./SPECIFICATION.md) for complete implementation details and requirements.

## License

This project is licensed under the terms specified in the LICENSE file in the root directory.

