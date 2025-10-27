# Token-Oriented Object Notation (TOON) for LLMs

Token-Oriented Object Notation (TOON) is an LLM-optimized data serialization format implemented in Python.

![Tests](https://img.shields.io/badge/tests-365%20passing-success)
![Coverage](https://img.shields.io/badge/coverage-83.46%25-success)
[![Python](https://img.shields.io/badge/python-3.11+-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-blue)](./LICENSE)

## ✨ Features

- 🎯 **LLM-optimized and Human-readable format**: More compact and easier to read than JSON
- 🐍 **Python-native**: Automatic handling of datetime, dataclasses, Pydantic models
- 📊 **Smart array formatting**: Inline, tabular, or list formats chosen automatically
- ⚙️ **Configurable**: Custom delimiters, indentation, and length markers
- 🔒 **Type-safe**: Full type hints and Pydantic validation
- 📝 **Data Science Compatible**: Compatible with JSON, Pandas and Pandas-like data tasks

Get more cognitive output and efficiency from LLMs with less tokens in prompts!

## 🚀 Quick Start

### Installation

```bash
# Using uv (recommended)
uv add toon-llm

# Using pip
pip install toon-llm
```

### Basic Usage

````python
from toon import encode, decode

# Encode Python data to TOON LLM format
data = {
    "username": "Alice",
    "age": 30,
    "tags": ["python", "coding", "llm"],
    "active": True,
    "invoices": [
        {"id": 1, "amount": 250.75, "paid": False},
        {"id": 2, "amount": 125.00, "paid": True},
        {"id": 3, "amount": 320.40, "paid": True},
        {"id": 4, "amount": 75.20, "paid": False},
        {"id": 5, "amount": 600.00, "paid": True}
    ]
}

encoded = encode(data)

# username: Alice
# age: 30
# tags[3]: python,coding,llm
# active: true
# invoices[5]{id,amount,paid}:
#   1,250.75,false
#   2,125,true
#   3,320.40,true
#   4,75.20,false
#   5,600,true

llm_prompt = f"""
Process the following structured data and return the invoices that have not been paid:
```
{encoded}
```
"""

# Call your LLM with llm_prompt...
````

### CLI Usage

TOON LLM includes a command-line interface for encoding and decoding data:

```bash
# Show help
uv run toon --help

# Encode JSON file to TOON format
uv run toon encode input.json -o output.toon

# Encode from stdin
echo '{"name": "Alice", "age": 30}' | uv run toon encode

# Decode TOON file to JSON
uv run toon decode input.toon -o output.json

# Decode with pretty printing
uv run toon decode input.toon --pretty

# Decode with validation
uv run toon decode input.toon --validate

# Custom formatting options
uv run toon encode input.json --indent 4 --delimiter "|"

# Show version
uv run toon --version
```

See `uv run toon encode --help` and `uv run toon decode --help` for all available options.

## 📖 Documentation

- **[Quick Start Guide](./docs/README.md)** - Examples and usage overview
- **[Format Specification](./specification/README.md)** - Token Oriented Object Notation (TOON) specification *(language agnostic)*
- **[API Reference](./docs/IMPLEMENTATION.md)** - Complete API documentation of the Python implementation
- **[LLM Prompts](./docs/LLM_PROMPTS.md)** - Guidance for LLMs to understand and generate TOON format
- **[Coding Standards](./docs/CODING_STANDARDS.md)** - For contributors

## 🎨 Why TOON LLM?

TOON LLM is a Python library that provides a clean, compact, and highly readable alternative to JSON for serializing Python data structures to minimise token usage with large language models (LLMs).

It is a Python compatible specification and implementation of [Token-Oriented Object Notation](https://github.com/johannschopplich/toon) format.

Cognitive load in LLMs can be significantly reduced by using more concise and structured data formats. TOON LLM achieves this by minimizing syntax noise and enhancing readability, making it easier for both humans and machines to parse and understand the data.

### Compare with JSON

Using the `cl100k_base` tokenizer from OpenAI, here is a comparison of how the same data is represented in JSON vs TOON LLM.

**JSON:**

```json
{
    "weather_observations": [
        { "high_temp": 75, "low_temp": 50, "average_temp": 62.5, "dew_point": 45, "wind_chill": 60 },
        { "high_temp": 78, "low_temp": 52, "average_temp": 65.0, "dew_point": 48, "wind_chill": 63 },
        { "high_temp": 72, "low_temp": 48, "average_temp": 60.0, "dew_point": 42, "wind_chill": 58 },
        { "high_temp": 80, "low_temp": 55, "average_temp": 67.5, "dew_point": 50, "wind_chill": 65 },
        { "high_temp": 76, "low_temp": 51, "average_temp": 63.5, "dew_point": 46, "wind_chill": 61 },
        { "high_temp": 74, "low_temp": 49, "average_temp": 61.5, "dew_point": 44, "wind_chill": 59 },
        { "high_temp": 79, "low_temp": 54, "average_temp": 66.5, "dew_point": 49, "wind_chill": 64 },
        { "high_temp": 73, "low_temp": 47, "average_temp": 60.0, "dew_point": 41, "wind_chill": 57 },
        { "high_temp": 77, "low_temp": 53, "average_temp": 65.0, "dew_point": 47, "wind_chill": 62 },
        { "high_temp": 81, "low_temp": 56, "average_temp": 68.5, "dew_point": 51, "wind_chill": 66 }
    ]
}
```

Token Count: **`411`**

**TOON LLM:**

```toon
weather_observations[10]:
  high_temp,low_temp,average_temp,dew_point,wind_chill
  75,50,62.5,45,60
  78,52,65.0,48,63
  72,48,60.0,42,58
  80,55,67.5,50,65
  76,51,63.5,46,61
  74,49,61.5,44,59
  79,54,66.5,49,64
  73,47,60.0,41,57
  77,53,65.0,47,62
  81,56,68.5,51,66
```

Token Count: **`162`**

That is over a 60% reduction in token count compared to JSON!

Multiply that over large datasets and complex structures, and the savings become substantial.

**Benefits:**

- ✨ Less syntax noise (no braces, fewer quotes)
- 📏 More compact (fewer lines and characters)
- 👁️ Easier to read and scan
- 🎯 Clear structure through indentation
- 📊 Smart array formatting (inline, tabular, or list)

### 🛠️ Configuration

TOON LLM provides flexible configuration options to customize the encoding format.

Read about them in the [Specification](./specification/README.md#configuration-options) and the [API Documentation](./docs/IMPLEMENTATION.md#configuration-options).

## 🧪 Testing

```bash
# Run tests
uv run pytest tests/ -v

# Run with coverage
uv run coverage run -m pytest && uv run coverage report

# Current status
# 310 tests passing
# 80.52% coverage
```

## 🤝 Contributing

Contributions are welcome! Please read our [Coding Standards](./docs/CODING_STANDARDS.md) before contributing.

### Development Setup

```bash
# Clone repository
git clone https://github.com/davidpirogov/toon-llm.git
cd toon-llm

# Install dependencies
uv sync

# Run tests
uv run pytest

# Run linting
uv run ruff check src/toon/

# Format code
uv run ruff format src/toon/
```

### Development Guidelines

1. Follow [PEP 8](https://peps.python.org/pep-0008/) and our [Coding Standards](./docs/CODING_STANDARDS.md)
2. Add tests for new features
3. Update documentation
4. Ensure all tests pass
5. Maintain or improve coverage

## 📋 Requirements

- Python 3.11 or higher
- Pydantic 2.x

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

## 🙏 Acknowledgments

Inspired by [Token-Oriented Object Notation](https://github.com/johannschopplich/toon) by Johann Schopplich.

If you are looking for a TypeScript/JavaScript implementation, check out [toon repository](https://github.com/johannschopplich/toon)

## 🔗 Links

- **GitHub**: [https://github.com/davidpirogov/toon-llm](https://github.com/davidpirogov/toon-llm)
- **Documentation**: [./docs/](./docs/)
- **Issues**: [GitHub Issues](https://github.com/davidpirogov/toon-llm/issues)
- **PyPI**: [https://pypi.org/project/toon-llm/](https://pypi.org/project/toon-llm/)
