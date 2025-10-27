# TOON Sample Files

This directory contains sample `.toon` files for testing the TOON LLM encoder.

## Directory Structure

```text
samples/
├── valid-simple/       # Simple, single-type valid TOON files
├── valid-complex/      # Complex, mixed-type valid TOON files
├── invalid-simple/     # Simple files with single format violations
├── invalid-complex/    # Complex files with multiple format violations
├── sample_data.py      # Python data structures for tests
├── INDEX.md            # Comprehensive file index
└── README.md           # This file
```

## File Naming Convention

- `{category}-{description}.toon`
- Valid files should encode correctly
- Invalid files should fail validation

## File Paths

All `.toon` files are organized into subdirectories:
- `valid-simple/valid-simple-*.toon`
- `valid-complex/valid-complex-*.toon`
- `invalid-simple/invalid-simple-*.toon`
- `invalid-complex/invalid-complex-*.toon`

## Usage

These files are used by the test suite to verify:
1. Correct encoding of Python data structures
2. Format compliance with TOON specification
3. Error detection for invalid formats
4. Edge cases and boundary conditions

### Example Usage

```python
from pathlib import Path
from toon import encode
from tests.samples import sample_data

# Test a valid simple sample
data = sample_data.get_valid_simple_sample("integer")
expected = Path("tests/samples/valid-simple/valid-simple-integer.toon").read_text()
assert encode(data) == expected

# Test an invalid sample
content = Path("tests/samples/invalid-simple/invalid-simple-trailing-space.toon").read_text()
assert content.endswith(" ")  # Verify it has the error
```
