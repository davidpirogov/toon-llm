# TOON Sample Files Index

## Overview

This directory contains **117 sample files** organized into four categories:

- **27 Valid Simple** - Single-type, straightforward examples
- **50 Valid Complex** - Multi-type, nested structures with various features
- **27 Invalid Simple** - Single format violations
- **20 Invalid Complex** - Multiple or subtle format violations

---

## Valid Simple Samples (27 files)

### Primitives (15)
- `valid-simple/valid-simple-null.toon` - Null value
- `valid-simple/valid-simple-bool-true.toon` - Boolean true
- `valid-simple/valid-simple-bool-false.toon` - Boolean false
- `valid-simple/valid-simple-integer.toon` - Positive integer
- `valid-simple/valid-simple-negative-integer.toon` - Negative integer
- `valid-simple/valid-simple-float.toon` - Floating point number
- `valid-simple/valid-simple-string-safe.toon` - Alphanumeric string (unquoted)
- `valid-simple/valid-simple-string-underscore.toon` - String with underscore
- `valid-simple/valid-simple-string-empty.toon` - Empty string (quoted)
- `valid-simple/valid-simple-string-with-spaces.toon` - String with spaces (quoted)
- `valid-simple/valid-simple-string-ambiguous-true.toon` - String "true" (quoted)
- `valid-simple/valid-simple-string-ambiguous-number.toon` - String "42" (quoted)
- `valid-simple/valid-simple-string-unicode.toon` - Unicode characters
- `valid-simple/valid-simple-string-emoji.toon` - Emoji character
- `valid-simple/valid-simple-string-control-chars.toon` - Escaped control characters
- `valid-simple/valid-simple-string-structural.toon` - Structural characters (quoted)

### Objects (5)
- `valid-simple/valid-simple-empty-object.toon` - Empty object
- `valid-simple/valid-simple-object-basic.toon` - Simple key-value pairs
- `valid-simple/valid-simple-object-with-null.toon` - Object with null value
- `valid-simple/valid-simple-object-quoted-key.toon` - Key with special chars
- `valid-simple/valid-simple-object-quoted-value.toon` - Value with special chars

### Arrays (7)
- `valid-simple/valid-simple-empty-array.toon` - Empty array
- `valid-simple/valid-simple-array-primitives.toon` - Array of numbers
- `valid-simple/valid-simple-array-strings.toon` - Array of strings
- `valid-simple/valid-simple-array-mixed.toon` - Mixed primitive types
- `valid-simple/valid-simple-array-with-quotes.toon` - Elements needing quotes
- `valid-simple/valid-simple-array-tabular.toon` - Tabular format (uniform objects)

---

## Valid Complex Samples (50 files)

### Nested Structures (11)
- `valid-complex/valid-complex-nested-object-with-arrays.toon` - Object with nested arrays
- `valid-complex/valid-complex-deep-nesting.toon` - 4-level deep nesting
- `valid-complex/valid-complex-tabular-with-floats.toon` - Tabular with float values
- `valid-complex/valid-complex-tabular-with-null.toon` - Tabular with null values
- `valid-complex/valid-complex-tabular-quoted-values.toon` - Tabular cells with delimiters
- `valid-complex/valid-complex-tabular-quoted-headers.toon` - Headers with special chars
- `valid-complex/valid-complex-array-of-arrays.toon` - Nested primitive arrays
- `valid-complex/valid-complex-list-format-different-keys.toon` - List format (non-uniform)
- `valid-complex/valid-complex-list-format-nested.toon` - List with nested objects
- `valid-complex/valid-complex-list-multiple-arrays.toon` - Object with multiple arrays
- `valid-complex/valid-complex-nested-tabular.toon` - Tabular array within object

### Root-Level Arrays (4)
- `valid-complex/valid-complex-root-primitive-array.toon` - Root-level primitive array
- `valid-complex/valid-complex-root-tabular.toon` - Root-level tabular array
- `valid-complex/valid-complex-root-list.toon` - Root-level list format
- `valid-complex/valid-complex-root-nested-arrays.toon` - Root-level nested arrays

### Mixed Types (1)
- `valid-complex/valid-complex-mixed-primitives-objects.toon` - Array mixing primitives and objects

### Custom Delimiters (8)
- `valid-complex/valid-complex-pipe-delimiter.toon` - Pipe delimiter (|)
- `valid-complex/valid-complex-tab-delimiter.toon` - Tab delimiter (\t)
- `valid-complex/valid-complex-tab-delimiter-no-comma-quoting.toon` - Tab: commas unquoted
- `valid-complex/valid-complex-tab-delimiter-aware-quoting.toon` - Tab: tabs quoted
- `valid-complex/valid-complex-pipe-delimiter-aware-quoting.toon` - Pipe: pipes quoted

### Length Markers (3)
- `valid-complex/valid-complex-length-marker.toon` - Length marker (#)
- `valid-complex/valid-complex-combined-options.toon` - Delimiter + length marker

### Real-World Examples (2)
- `valid-complex/valid-complex-real-world-company.toon` - Company data structure
- `valid-complex/valid-complex-real-world-products.toon` - Product catalog

---

## Invalid Simple Samples (27 files)

### Format Violations (8)
- `invalid-simple/invalid-simple-trailing-space.toon` - Line ends with space
- `invalid-simple/invalid-simple-trailing-newline.toon` - File ends with newline
- `invalid-simple/invalid-simple-wrong-indent.toon` - Incorrect indentation
- `invalid-simple/invalid-simple-odd-indent-spaces.toon` - Odd number of indent spaces

### Object Errors (5)
- `invalid-simple/invalid-simple-missing-colon.toon` - Key without `:` separator
- `invalid-simple/invalid-simple-missing-key.toon` - `:` without key
- `invalid-simple/invalid-simple-unquoted-special-key.toon` - Special char in key unquoted
- `invalid-simple/invalid-simple-unquoted-comma-value.toon` - Comma in value unquoted
- `invalid-simple/invalid-simple-ambiguous-string-unquoted.toon` - "true" string unquoted
- `invalid-simple/invalid-simple-unescaped-newline.toon` - Newline not escaped

### Array Errors (9)
- `invalid-simple/invalid-simple-array-missing-colon.toon` - Array header without `:`
- `invalid-simple/invalid-simple-array-wrong-length.toon` - Length ≠ item count
- `invalid-simple/invalid-simple-array-trailing-comma.toon` - Trailing comma
- `invalid-simple/invalid-simple-array-leading-comma.toon` - Leading comma
- `invalid-simple/invalid-simple-array-spaces-after-delimiter.toon` - Spaces after delimiter
- `invalid-simple/invalid-simple-array-unquoted-structural.toon` - `[` not quoted in value

### Tabular Errors (5)
- `invalid-simple/invalid-simple-tabular-missing-colon.toon` - Header without `:`
- `invalid-simple/invalid-simple-tabular-missing-indent.toon` - Rows not indented
- `invalid-simple/invalid-simple-tabular-wrong-column-count.toon` - Row column mismatch
- `invalid-simple/invalid-simple-tabular-wrong-row-count.toon` - Row count mismatch
- `invalid-simple/invalid-simple-tabular-header-no-comma.toon` - Header fields not delimited

### List Format Errors (4)
- `invalid-simple/invalid-simple-list-missing-colon.toon` - List header without `:`
- `invalid-simple/invalid-simple-list-missing-hyphen.toon` - Items without `-` prefix
- `invalid-simple/invalid-simple-list-hyphen-no-space.toon` - No space after `-`
- `invalid-simple/invalid-simple-list-wrong-continuation-indent.toon` - Wrong continuation indent

### Options Errors (2)
- `invalid-simple/invalid-simple-mixed-delimiters.toon` - Inconsistent delimiter use
- `invalid-simple/invalid-simple-length-marker-mismatch.toon` - Length marker inconsistency

---

## Invalid Complex Samples (20 files)

### Structural Errors (5)
- `invalid-complex/invalid-complex-nested-trailing-space.toon` - Trailing space in nested
- `invalid-complex/invalid-complex-broken-nesting.toon` - Broken nesting structure
- `invalid-complex/invalid-complex-extra-blank-lines.toon` - Extra blank lines
- `invalid-complex/invalid-complex-mixed-indent-levels.toon` - Inconsistent indentation
- `invalid-complex/invalid-complex-mixed-list-structure-error.toon` - Mixed list structure

### Tabular Errors (7)
- `invalid-complex/invalid-complex-tabular-length-mismatch.toon` - 3 rows but header says 2
- `invalid-complex/invalid-complex-tabular-inconsistent-columns.toon` - Different column counts
- `invalid-complex/invalid-complex-tabular-wrong-row-indent.toon` - Row indented wrong
- `invalid-complex/invalid-complex-tabular-inconsistent-header-quoting.toon` - Inconsistent quotes
- `invalid-complex/invalid-complex-tabular-quoted-row-as-single.toon` - Entire row quoted
- `invalid-complex/invalid-complex-tabular-unquoted-special-value.toon` - Special char unquoted
- `invalid-complex/invalid-complex-nested-tabular-wrong-indent.toon` - Nested table wrong indent

### List Format Errors (2)
- `invalid-complex/invalid-complex-list-indent-mismatch.toon` - Continuation wrong indent
- `invalid-complex/invalid-complex-list-missing-hyphen-continuation.toon` - Missing hyphen

### Array Errors (3)
- `invalid-complex/invalid-complex-nested-array-wrong-length.toon` - Nested array length wrong
- `invalid-complex/invalid-complex-nested-array-length-mismatch.toon` - Object array length wrong
- `invalid-complex/invalid-complex-root-array-length-mismatch.toon` - Root array length wrong
- `invalid-complex/invalid-complex-deeply-nested-length-error.toon` - Deep nested length error

### Options Errors (3)
- `invalid-complex/invalid-complex-delimiter-inconsistency.toon` - Mixed delimiters
- `invalid-complex/invalid-complex-length-marker-inconsistency.toon` - Inconsistent markers

---

## Usage in Tests

### Testing Valid Files
```python
from pathlib import Path
from toon import encode
from tests.samples.sample_data import get_valid_simple_sample

def test_valid_simple_integer():
    data = get_valid_simple_sample("integer")
    expected = Path("tests/samples/valid-simple/valid-simple-integer.toon").read_text()
    assert encode(data) == expected
```

### Testing Invalid Files
```python
from pathlib import Path

def test_invalid_simple_trailing_space():
    content = Path("tests/samples/invalid-simple/invalid-simple-trailing-space.toon").read_text()
    # This content should NOT be producible by encode()
    # or should fail validation if we build a parser
    assert content.endswith(" ")  # Verify it has the error
```

### Parameterized Testing
```python
import pytest
from tests.samples.sample_data import list_all_valid_samples

@pytest.mark.parametrize("sample_name", list_all_valid_samples())
def test_all_valid_samples(sample_name):
    # Test each valid sample
    ...
```

---

## File Organization Summary

```
tests/samples/
├── valid-simple/                          # Simple valid files
│   └── valid-simple-*.toon               # 27 files
├── valid-complex/                         # Complex valid files
│   └── valid-complex-*.toon              # 50 files
├── invalid-simple/                        # Simple invalid files
│   └── invalid-simple-*.toon             # 27 files
├── invalid-complex/                       # Complex invalid files
│   └── invalid-complex-*.toon            # 20 files
├── sample_data.py                         # Python data structures
├── INDEX.md                               # This file
└── README.md                              # Overview documentation
```

**Total: 127 files** (99 .toon files + 3 Python/documentation files + 4 directories)
