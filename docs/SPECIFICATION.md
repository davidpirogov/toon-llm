# PyToon Specification

## Overview

PyToon is a Python library for encoding Python data structures into a compact, human-readable text format. This specification defines the encoding rules and behavior.

## Table of Contents

1. [Core Function](#core-function)
2. [Primitive Types](#primitive-types)
3. [Objects (Dictionaries)](#objects-dictionaries)
4. [Arrays (Lists)](#arrays-lists)
5. [Complex Structures](#complex-structures)
6. [Configuration Options](#configuration-options)
7. [Non-Serializable Values](#non-serializable-values)

---

## Core Function

### Function Signature

```python
def encode(data: Any, *, delimiter: str = ',', length_marker: str = '') -> str:
    """
    Encode Python data structures into a compact text format.

    Args:
        data: Any Python object to encode
        delimiter: Character(s) used to separate array elements (default: ',')
        length_marker: Optional prefix for array length indicators (default: '')

    Returns:
        A string representation of the data
    """
```

---

## Primitive Types

### Strings

#### Safe Strings

- **Rule**: Alphanumeric strings and underscores are encoded without quotes
- **Examples**:
    - `'hello'` → `'hello'`
    - `'Ada_99'` → `'Ada_99'`

#### Empty String

- **Rule**: Empty string must be quoted
- **Example**: `''` → `'""'`

#### Ambiguous Strings

- **Rule**: Strings that look like booleans, null, or numbers must be quoted
- **Examples**:
    - `'true'` → `'"true"'`
    - `'false'` → `'"false"'`
    - `'null'` → `'"null"'`
    - `'42'` → `'"42"'`
    - `'-3.14'` → `'"-3.14"'`
    - `'1e-6'` → `'"1e-6"'`
    - `'05'` → `'"05"'` (leading zero)

#### Control Characters

- **Rule**: Control characters must be escaped within quotes
- **Examples**:
    - `'line1\nline2'` → `'"line1\\nline2"'`
    - `'tab\there'` → `'"tab\\there"'`
    - `'return\rcarriage'` → `'"return\\rcarriage"'`
    - `'C:\\Users\\path'` → `'"C:\\\\Users\\\\path"'`

#### Structural Characters

- **Rule**: Strings containing structural characters must be quoted
- **Examples**:
    - `'[3]: x,y'` → `'"[3]: x,y"'`
    - `'- item'` → `'"- item"'`
    - `'[test]'` → `'"[test]"'`
    - `'{key}'` → `'"{key}"'`

#### Unicode and Emoji

- **Rule**: Unicode characters and emoji are preserved as-is
- **Examples**:
    - `'café'` → `'café'`
    - `'你好'` → `'你好'`
    - `'🚀'` → `'🚀'`
    - `'hello 👋 world'` → `'hello 👋 world'`

#### Whitespace

- **Rule**: Strings with leading/trailing spaces must be quoted
- **Examples**:
    - `' padded '` → `'" padded "'`
    - `'  '` → `'"  "'`

### Numbers

#### Integer and Float

- **Rule**: Numbers are encoded as strings without quotes
- **Examples**:
    - `42` → `'42'`
    - `3.14` → `'3.14'`
    - `-7` → `'-7'`
    - `0` → `'0'`

#### Special Numeric Values

- **Rule**: Special numeric handling
- **Examples**:
    - `-0` → `'0'` (negative zero becomes positive)
    - `1e6` → `'1000000'` (scientific notation expanded)
    - `1e-6` → `'0.000001'`
    - `1e20` → `'100000000000000000000'`
    - `Number.MAX_SAFE_INTEGER` → `'9007199254740991'`

#### Non-Finite Numbers

- **Rule**: Non-finite numbers become null
- **Examples**:
    - `Infinity` → `'null'`
    - `-Infinity` → `'null'`
    - `NaN` → `'null'`

### Booleans

- **Rule**: Booleans are lowercase strings without quotes
- **Examples**:
    - `True` → `'true'`
    - `False` → `'false'`

### None (Null)

- **Rule**: None is encoded as 'null' without quotes
- **Example**: `None` → `'null'`

---

## Objects (Dictionaries)

### Simple Objects

#### Basic Key-Value Pairs

- **Rule**: Keys and values separated by `: `, entries separated by newlines
- **Rule**: Key order is preserved
- **Example**:
    ```python
    {'id': 123, 'name': 'Ada', 'active': True}
    ```
    →
    ```
    id: 123
    name: Ada
    active: true
    ```

#### Empty Objects

- **Rule**: Empty dictionaries encode as empty string
- **Example**: `{}` → `''`

#### Null Values

- **Rule**: None values are encoded as 'null'
- **Example**:
    ```python
    {'id': 123, 'value': None}
    ```
    →
    ```
    id: 123
    value: null
    ```

### Key Quoting

#### Special Characters in Keys

- **Rule**: Keys containing special characters must be quoted
- **Examples**:
    - `{'order:id': 7}` → `'"order:id": 7'`
    - `{'[index]': 5}` → `'"[index]": 5'`
    - `{'{key}': 5}` → `'"{key}": 5'`
    - `{'a,b': 1}` → `'"a,b": 1'`

#### Whitespace and Leading Hyphens

- **Rule**: Keys with spaces or leading hyphens must be quoted
- **Examples**:
    - `{'full name': 'Ada'}` → `'"full name": Ada'`
    - `{'-lead': 1}` → `'"-lead": 1'`
    - `{' a ': 1}` → `'" a ": 1'`

#### Numeric Keys

- **Rule**: Numeric keys must be quoted
- **Example**: `{123: 'x'}` → `'"123": x'`

#### Empty Key

- **Rule**: Empty string key must be quoted
- **Example**: `{'': 1}` → `'"": 1'`

#### Control Characters in Keys

- **Rule**: Control characters in keys must be escaped
- **Examples**:
    - `{'line\nbreak': 1}` → `'"line\\nbreak": 1'`
    - `{'tab\there': 2}` → `'"tab\\there": 2'`

#### Quotes in Keys

- **Rule**: Quotes in keys must be escaped
- **Example**: `{'he said "hi"': 1}` → `'"he said \\"hi\\"": 1'`

### Value Quoting

#### Special Characters in Values

- **Rule**: String values with special characters must be quoted
- **Examples**:
    - `{'note': 'a:b'}` → `'note: "a:b"'`
    - `{'note': 'a,b'}` → `'note: "a,b"'`
    - `{'text': 'line1\nline2'}` → `'text: "line1\\nline2"'`
    - `{'text': 'say "hello"'}` → `'text: "say \\"hello\\""'`

### Nested Objects

#### Deeply Nested

- **Rule**: Nested objects are indented with 2 spaces per level
- **Example**:
    ```python
    {'a': {'b': {'c': 'deep'}}}
    ```
    →
    ```
    a:
      b:
        c: deep
    ```

#### Empty Nested Object

- **Rule**: Empty nested objects show key with colon only
- **Example**: `{'user': {}}` → `'user:'`

---

## Arrays (Lists)

### Primitive Arrays

#### Inline Format

- **Rule**: Arrays of primitives are encoded inline with `[length]: item1,item2,...`
- **Examples**:
    - `{'tags': ['reading', 'gaming']}` → `'tags[2]: reading,gaming'`
    - `{'nums': [1, 2, 3]}` → `'nums[3]: 1,2,3'`
    - `{'data': ['x', 'y', True, 10]}` → `'data[4]: x,y,true,10'`

#### Empty Arrays

- **Rule**: Empty arrays show `[0]:` with no values
- **Example**: `{'items': []}` → `'items[0]:'`

#### Empty Strings in Arrays

- **Rule**: Empty strings must be quoted
- **Examples**:
    - `{'items': ['']}` → `'items[1]: ""'`
    - `{'items': ['a', '', 'b']}` → `'items[3]: a,"",b'`

#### Whitespace in Arrays

- **Rule**: Whitespace-only strings must be quoted
- **Example**: `{'items': [' ', '  ']}` → `'items[2]: " ","  "'`

#### Special Characters in Array Elements

- **Rule**: Array elements with special characters must be quoted
- **Examples**:
    - `{'items': ['a', 'b,c', 'd:e']}` → `'items[3]: a,"b,c","d:e"'`
    - `{'items': ['x', 'true', '42', '-3.14']}` → `'items[4]: x,"true","42","-3.14"'`
    - `{'items': ['[5]', '- item', '{key}']}` → `'items[3]: "[5]","- item","{key}"'`

### Arrays of Objects

#### Tabular Format

- **Rule**: Arrays of objects with identical keys use tabular format
- **Rule**: Format: `key[length]{field1,field2,...}:\n  val1,val2,...`
- **Example**:
    ```python
    {
      'items': [
        {'sku': 'A1', 'qty': 2, 'price': 9.99},
        {'sku': 'B2', 'qty': 1, 'price': 14.5}
      ]
    }
    ```
    →
    ```
    items[2]{sku,qty,price}:
      A1,2,9.99
      B2,1,14.5
    ```

#### Null in Tabular Format

- **Rule**: Null values are represented as 'null' in tables
- **Example**:
    ```python
    {
      'items': [
        {'id': 1, 'value': None},
        {'id': 2, 'value': 'test'}
      ]
    }
    ```
    →
    ```
    items[2]{id,value}:
      1,null
      2,test
    ```

#### Quoted Values in Tables

- **Rule**: Tabular values containing delimiters must be quoted
- **Example**:
    ```python
    {
      'items': [
        {'sku': 'A,1', 'desc': 'cool', 'qty': 2},
        {'sku': 'B2', 'desc': 'wip: test', 'qty': 1}
      ]
    }
    ```
    →
    ```
    items[2]{sku,desc,qty}:
      "A,1",cool,2
      B2,"wip: test",1
    ```

#### Quoted Keys in Tabular Headers

- **Rule**: Header keys with special characters must be quoted
- **Example**:
    ```python
    {
      'items': [
        {'order:id': 1, 'full name': 'Ada'},
        {'order:id': 2, 'full name': 'Bob'}
      ]
    }
    ```
    →
    ```
    items[2]{"order:id","full name"}:
      1,Ada
      2,Bob
    ```

#### Field Order in Tabular Format

- **Rule**: Use field order from first object for all rows
- **Example**:
    ```python
    {
      'items': [
        {'a': 1, 'b': 2, 'c': 3},
        {'c': 30, 'b': 20, 'a': 10}  # Different order
      ]
    }
    ```
    →
    ```
    items[2]{a,b,c}:
      1,2,3
      10,20,30
    ```

#### List Format (Different Keys)

- **Rule**: Arrays of objects with different keys use list format with `- ` prefix
- **Example**:
    ```python
    {
      'items': [
        {'id': 1, 'name': 'First'},
        {'id': 2, 'name': 'Second', 'extra': True}
      ]
    }
    ```
    →
    ```
    items[2]:
      - id: 1
        name: First
      - id: 2
        name: Second
        extra: true
    ```

#### List Format (Nested Values)

- **Rule**: Arrays containing objects with nested values use list format
- **Example**:
    ```python
    {
      'items': [
        {'id': 1, 'nested': {'x': 1}}
      ]
    }
    ```
    →
    ```
    items[1]:
      - id: 1
        nested:
          x: 1
    ```

#### List Format (Mixed Value Types)

- **Rule**: If any object has both primitive and non-primitive values at different positions, use list format
- **Example**:
    ```python
    {
      'items': [
        {'id': 1, 'data': 'string'},
        {'id': 2, 'data': {'nested': True}}
      ]
    }
    ```
    →
    ```
    items[2]:
      - id: 1
        data: string
      - id: 2
        data:
          nested: true
    ```

#### Field Order in List Items

- **Rule**: Preserve original field order in each list item
- **Examples**:

    ```python
    {'items': [{'nums': [1, 2, 3], 'name': 'test'}]}
    ```

    →

    ```
    items[1]:
      - nums[3]: 1,2,3
        name: test
    ```

    ```python
    {'items': [{'name': 'test', 'nums': [1, 2, 3]}]}
    ```

    →

    ```
    items[1]:
      - name: test
        nums[3]: 1,2,3
    ```

#### Arrays of Arrays in Objects

- **Rule**: Objects containing arrays of arrays use list format
- **Example**:
    ```python
    {
      'items': [
        {'matrix': [[1, 2], [3, 4]], 'name': 'grid'}
      ]
    }
    ```
    →
    ```
    items[1]:
      - matrix[2]:
        - [2]: 1,2
        - [2]: 3,4
        name: grid
    ```

#### Nested Tabular Arrays

- **Rule**: Nested arrays of uniform objects can use tabular format
- **Example**:
    ```python
    {
      'items': [
        {
          'users': [{'id': 1, 'name': 'Ada'}, {'id': 2, 'name': 'Bob'}],
          'status': 'active'
        }
      ]
    }
    ```
    →
    ```
    items[1]:
      - users[2]{id,name}:
        1,Ada
        2,Bob
        status: active
    ```

#### Nested List Arrays

- **Rule**: Nested arrays with mismatched keys use list format
- **Example**:
    ```python
    {
      'items': [
        {
          'users': [{'id': 1, 'name': 'Ada'}, {'id': 2}],
          'status': 'active'
        }
      ]
    }
    ```
    →
    ```
    items[1]:
      - users[2]:
        - id: 1
          name: Ada
        - id: 2
        status: active
    ```

#### Multiple Array Fields

- **Rule**: Objects with multiple array fields use list format
- **Example**:
    ```python
    {
      'items': [
        {'nums': [1, 2], 'tags': ['a', 'b'], 'name': 'test'}
      ]
    }
    ```
    →
    ```
    items[1]:
      - nums[2]: 1,2
        tags[2]: a,b
        name: test
    ```

#### Empty Arrays in List Format

- **Rule**: Empty arrays in list items show `[0]:`
- **Example**:
    ```python
    {
      'items': [
        {'name': 'test', 'data': []}
      ]
    }
    ```
    →
    ```
    items[1]:
      - name: test
        data[0]:
    ```

#### First Field on Hyphen Line

- **Rule**: For nested tabular arrays, first field goes on same line as hyphen
- **Example**:
    ```python
    {
      'items': [
        {'users': [{'id': 1}, {'id': 2}], 'note': 'x'}
      ]
    }
    ```
    →
    ```
    items[1]:
      - users[2]{id}:
        1
        2
        note: x
    ```

#### Empty Arrays on Hyphen Line

- **Rule**: Empty arrays placed on hyphen line when first field
- **Example**:
    ```python
    {'items': [{'data': [], 'name': 'x'}]}
    ```
    →
    ```
    items[1]:
      - data[0]:
        name: x
    ```

### Arrays of Arrays

#### Nested Primitive Arrays

- **Rule**: Arrays of primitive arrays use list format with `- [length]: items`
- **Example**:
    ```python
    {
      'pairs': [['a', 'b'], ['c', 'd']]
    }
    ```
    →
    ```
    pairs[2]:
      - [2]: a,b
      - [2]: c,d
    ```

#### Quoted Values in Nested Arrays

- **Rule**: Values with delimiters must be quoted
- **Example**:
    ```python
    {
      'pairs': [['a', 'b'], ['c,d', 'e:f', 'true']]
    }
    ```
    →
    ```
    pairs[2]:
      - [2]: a,b
      - [3]: "c,d","e:f","true"
    ```

#### Empty Inner Arrays

- **Rule**: Empty inner arrays show `[0]:`
- **Example**:
    ```python
    {'pairs': [[], []]}
    ```
    →
    ```
    pairs[2]:
      - [0]:
      - [0]:
    ```

#### Mixed-Length Inner Arrays

- **Rule**: Each inner array shows its own length
- **Example**:
    ```python
    {'pairs': [[1], [2, 3]]}
    ```
    →
    ```
    pairs[2]:
      - [1]: 1
      - [2]: 2,3
    ```

### Root Arrays

#### Root Primitive Arrays

- **Rule**: Root-level arrays use `[length]: items` format
- **Example**:
    ```python
    ['x', 'y', 'true', True, 10]
    ```
    →
    ```
    [5]: x,y,"true",true,10
    ```

#### Root Tabular Arrays

- **Rule**: Root arrays of uniform objects use tabular format
- **Example**:
    ```python
    [{'id': 1}, {'id': 2}]
    ```
    →
    ```
    [2]{id}:
      1
      2
    ```

#### Root List Arrays

- **Rule**: Root arrays of non-uniform objects use list format
- **Example**:
    ```python
    [{'id': 1}, {'id': 2, 'name': 'Ada'}]
    ```
    →
    ```
    [2]:
      - id: 1
      - id: 2
        name: Ada
    ```

#### Root Empty Arrays

- **Rule**: Empty root arrays encode as `[0]:`
- **Example**: `[]` → `'[0]:'`

#### Root Nested Arrays

- **Rule**: Root arrays of arrays use list format
- **Example**:
    ```python
    [[1, 2], []]
    ```
    →
    ```
    [2]:
      - [2]: 1,2
      - [0]:
    ```

### Mixed Arrays

#### Primitives and Objects

- **Rule**: Arrays mixing primitives and objects use list format
- **Example**:
    ```python
    {
      'items': [1, {'a': 1}, 'text']
    }
    ```
    →
    ```
    items[3]:
      - 1
      - a: 1
      - text
    ```

#### Objects and Arrays

- **Rule**: Arrays mixing objects and arrays use list format
- **Example**:
    ```python
    {
      'items': [{'a': 1}, [1, 2]]
    }
    ```
    →
    ```
    items[2]:
      - a: 1
      - [2]: 1,2
    ```

---

## Complex Structures

### Mixed Nested Structures

- **Rule**: Complex structures combine all rules appropriately
- **Example**:
    ```python
    {
      'user': {
        'id': 123,
        'name': 'Ada',
        'tags': ['reading', 'gaming'],
        'active': True,
        'prefs': []
      }
    }
    ```
    →
    ```
    user:
      id: 123
      name: Ada
      tags[2]: reading,gaming
      active: true
      prefs[0]:
    ```

---

## Configuration Options

### Delimiter Option

#### Purpose

- **Rule**: Allows customization of the array separator character
- **Default**: `','` (comma)
- **Supported Values**: `','`, `'|'`, `'\t'` (tab), or custom strings

#### Primitive Arrays

- **Rule**: Delimiter is used between array elements
- **Rule**: Delimiter appears in length marker if not comma
- **Examples**:
    - Tab: `{'tags': ['reading', 'gaming', 'coding']}` with `delimiter='\t'` → `'tags[3\t]: reading\tgaming\tcoding'`
    - Pipe: `{'tags': ['reading', 'gaming', 'coding']}` with `delimiter='|'` → `'tags[3|]: reading|gaming|coding'`
    - Comma (default): `{'tags': ['reading', 'gaming', 'coding']}` → `'tags[3]: reading,gaming,coding'`

#### Tabular Arrays

- **Rule**: Delimiter separates header fields and row values
- **Examples**:
    - Tab:
        ```python
        {
          'items': [
            {'sku': 'A1', 'qty': 2, 'price': 9.99},
            {'sku': 'B2', 'qty': 1, 'price': 14.5}
          ]
        }
        ```
        with `delimiter='\t'` →
        ```
        items[2	]{sku	qty	price}:
          A1	2	9.99
          B2	1	14.5
        ```
    - Pipe:
        ```
        items[2|]{sku|qty|price}:
          A1|2|9.99
          B2|1|14.5
        ```

#### Nested Arrays

- **Rule**: Delimiter is used consistently throughout nested structures
- **Examples**:
    - Tab: `{'pairs': [['a', 'b'], ['c', 'd']]}` with `delimiter='\t'` →
        ```
        pairs[2	]:
          - [2	]: a	b
          - [2	]: c	d
        ```
    - Pipe: →
        ```
        pairs[2|]:
          - [2|]: a|b
          - [2|]: c|d
        ```

#### Root Arrays

- **Rule**: Delimiter applies to root-level arrays
- **Examples**:
    - Tab: `['x', 'y', 'z']` with `delimiter='\t'` → `'[3\t]: x\ty\tz'`
    - Pipe: `['x', 'y', 'z']` with `delimiter='|'` → `'[3|]: x|y|z'`

#### Delimiter-Aware Quoting

- **Rule**: Strings containing the active delimiter must be quoted
- **Examples**:
    - Tab delimiter: `{'items': ['a', 'b\tc', 'd']}` with `delimiter='\t'` → `'items[3\t]: a\t"b\\tc"\td'`
    - Pipe delimiter: `{'items': ['a', 'b|c', 'd']}` with `delimiter='|'` → `'items[3|]: a|"b|c"|d'`

#### Delimiter Independence for Commas

- **Rule**: Commas don't need quoting when delimiter is not comma
- **Examples**:
    - Tab: `{'items': ['a,b', 'c,d']}` with `delimiter='\t'` → `'items[2\t]: a,b\tc,d'`
    - Pipe: `{'items': ['a,b', 'c,d']}` with `delimiter='|'` → `'items[2|]: a,b|c,d'`

#### Delimiter in Object Values

- **Rule**: Object values with delimiter must be quoted if delimiter is comma
- **Examples**:
    - Comma: `{'note': 'a,b'}` → `'note: "a,b"'`
    - Pipe: `{'note': 'a,b'}` with `delimiter='|'` → `'note: a,b'`
    - Tab: `{'note': 'a,b'}` with `delimiter='\t'` → `'note: a,b'`

#### Delimiter in Tabular Values

- **Rule**: Tabular cell values containing delimiter must be quoted
- **Example**:
    ```python
    {
      'items': [
        {'id': 1, 'note': 'a,b'},
        {'id': 2, 'note': 'c,d'}
      ]
    }
    ```

    - Comma: →
        ```
        items[2]{id,note}:
          1,"a,b"
          2,"c,d"
        ```
    - Tab with `delimiter='\t'`: →
        ```
        items[2	]{id	note}:
          1	a,b
          2	c,d
        ```

#### Delimiter in Keys

- **Rule**: Keys containing the delimiter must be quoted
- **Examples**:
    - Pipe: `{'a|b': 1}` with `delimiter='|'` → `'"a|b": 1'`
    - Tab: `{'a\tb': 1}` with `delimiter='\t'` → `'"a\\tb": 1'`

#### Delimiter in Tabular Headers

- **Rule**: Header keys containing delimiter must be quoted
- **Example**:
    ```python
    {'items': [{'a|b': 1}, {'a|b': 2}]}
    ```
    with `delimiter='|'` →
    ```
    items[2|]{"a|b"}:
      1
      2
    ```

#### Delimiter-Independent Quoting

- **Rule**: Ambiguous strings, structural characters, etc. are quoted regardless of delimiter
- **Examples**:
    - `{'items': ['true', '42', '-3.14']}` with any delimiter → quotes preserved
    - `{'items': ['[5]', '{key}', '- item']}` with any delimiter → quotes preserved

### Length Marker Option

#### Purpose

- **Rule**: Adds an optional prefix character to array length indicators
- **Default**: `''` (no prefix)
- **Common Value**: `'#'`

#### Primitive Arrays

- **Rule**: Marker prefixes the length number
- **Example**: `{'tags': ['reading', 'gaming', 'coding']}` with `length_marker='#'` → `'tags[#3]: reading,gaming,coding'`

#### Empty Arrays

- **Rule**: Marker applies to empty arrays
- **Example**: `{'items': []}` with `length_marker='#'` → `'items[#0]:'`

#### Tabular Arrays

- **Rule**: Marker prefixes length in tabular headers
- **Example**:
    ```python
    {
      'items': [
        {'sku': 'A1', 'qty': 2, 'price': 9.99},
        {'sku': 'B2', 'qty': 1, 'price': 14.5}
      ]
    }
    ```
    with `length_marker='#'` →
    ```
    items[#2]{sku,qty,price}:
      A1,2,9.99
      B2,1,14.5
    ```

#### Nested Arrays

- **Rule**: Marker applies to all array levels
- **Example**: `{'pairs': [['a', 'b'], ['c', 'd']]}` with `length_marker='#'` →
    ```
    pairs[#2]:
      - [#2]: a,b
      - [#2]: c,d
    ```

#### Combined with Delimiter

- **Rule**: Length marker can be combined with custom delimiter
- **Example**: `{'tags': ['reading', 'gaming', 'coding']}` with `length_marker='#'` and `delimiter='|'` → `'tags[#3|]: reading|gaming|coding'`

---

## Non-Serializable Values

### BigInt (Python: Large Integers)

- **Rule**: Large integers are converted to string representation
- **Examples** (TypeScript equivalent):
    - `BigInt(123)` → `'123'`
    - `{'id': BigInt(456)}` → `'id: 456'`

### Date/Datetime Objects

- **Rule**: Date objects are converted to ISO 8601 string format and quoted
- **Examples**:
    - `datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc)` → `'"2025-01-01T00:00:00.000Z"'`
    - `{'created': datetime(...)}` → `'created: "2025-01-01T00:00:00.000Z"'`

### Undefined/Missing Values

- **Rule**: Python doesn't have `undefined`, but explicit `None` converts to `null`
- **Examples**:
    - `None` → `'null'`
    - `{'value': None}` → `'value: null'`

### Functions/Callables

- **Rule**: Functions and callable objects are converted to `null`
- **Examples**:
    - `lambda: None` → `'null'`
    - `{'fn': lambda: None}` → `'fn: null'`

### Symbols (Python: No Direct Equivalent)

- **Rule**: If custom symbol-like objects are used, convert to `null`
- **Note**: Python doesn't have JavaScript Symbol type

---

## Formatting Invariants

### No Trailing Spaces

- **Rule**: Lines must not end with trailing whitespace
- **Verification**: All output lines are checked to ensure no trailing spaces

### No Trailing Newline

- **Rule**: Output must not end with a newline character
- **Verification**: Output string must not match `/\n$/`

### Indentation

- **Rule**: Nested structures use 2 spaces per level
- **Rule**: List items use 2-space indent plus `- ` for first line
- **Rule**: Subsequent fields in list items align with first field (4 spaces total)

### Line Separation

- **Rule**: Top-level dictionary entries are separated by newlines
- **Rule**: Array items in list format are separated by newlines
- **Rule**: Tabular array rows each on separate line with 2-space indent

---

## Python-Specific Implementation Notes

### Type Hints

- Use comprehensive type hints for all function parameters and return values
- Consider using `typing.Protocol` for structural typing where appropriate
- Use `typing.Literal` for delimiter and length_marker options

### Data Structure Mapping

- JavaScript Object → Python `dict`
- JavaScript Array → Python `list`
- JavaScript `null` → Python `None`
- JavaScript `undefined` → Python `None` (explicit)
- JavaScript number → Python `int` or `float`
- JavaScript boolean → Python `bool`
- JavaScript string → Python `str`

### Special Considerations

- Python's `-0` and `0` are the same, so no special handling needed
- Use `math.isfinite()` to check for `inf` and `nan`
- Use `isinstance()` for type checking
- Use `collections.abc` for abstract type checking
- Consider using `dataclasses` for internal state management if needed

### Testing Framework

- Use `pytest` for unit testing
- Maintain 1:1 correspondence with TypeScript test cases
- Use parametrized tests for delimiter and length_marker options

### String Handling

- Use raw strings (`r""`) for escape sequence literals in tests
- Use `repr()` or custom quoting logic for string encoding
- Handle Unicode properly (Python 3 handles this natively)

### Performance Considerations

- Use `io.StringIO` for building output strings efficiently
- Consider caching key quoting decisions for repeated keys
- Use generator expressions where appropriate

---

## API Design

### Main Function

```python
def encode(
    data: Any,
    *,
    delimiter: str = ',',
    length_marker: str = ''
) -> str:
    """
    Encode Python data structures into a compact text format.

    Args:
        data: The Python object to encode. Can be any JSON-serializable type
              plus datetime, large integers, and other special types.
        delimiter: Character(s) to use as array element separator.
                   Default is ','. Common alternatives: '|', '\t'.
        length_marker: Optional prefix for array length indicators.
                      Default is '' (no prefix). Common value: '#'.

    Returns:
        A string representation of the data in the compact format.

    Raises:
        TypeError: If data contains unsupported types (after conversion attempts).

    Examples:
        >>> encode({'name': 'Ada', 'age': 42})
        'name: Ada\\nage: 42'

        >>> encode([1, 2, 3])
        '[3]: 1,2,3'

        >>> encode({'items': [{'id': 1}, {'id': 2}]})
        'items[2]{id}:\\n  1\\n  2'

        >>> encode(['a', 'b', 'c'], delimiter='|')
        '[3|]: a|b|c'

        >>> encode([1, 2, 3], length_marker='#')
        '[#3]: 1,2,3'
    """
```

### Helper Functions (Internal)

The implementation will likely need several internal helper functions:

- `_normalize_value(value)`: Convert non-serializable values to serializable equivalents
- `_needs_quoting(s, context)`: Determine if a string needs quotes
- `_quote_string(s)`: Add quotes and escape characters
- `_encode_primitive(value, context)`: Encode primitive types
- `_encode_dict(obj, indent, context)`: Encode dictionary objects
- `_encode_list(arr, key, indent, context)`: Encode list/arrays
- `_is_primitive_array(arr)`: Check if array contains only primitives
- `_can_use_tabular(arr)`: Check if array of objects can use tabular format
- `_get_object_keys(objects)`: Extract unified key set from objects
- `_encode_tabular(arr, key, indent, context)`: Encode in tabular format
- `_encode_list_format(arr, key, indent, context)`: Encode in list format

### Context Object

Consider using a context dataclass to pass encoding parameters:

```python
@dataclass
class EncodingContext:
    delimiter: str
    length_marker: str

    def array_header(self, length: int) -> str:
        """Generate array length marker: [#3|] or [3] etc."""
        ...

    def needs_quoting(self, s: str, location: str) -> bool:
        """Check if string needs quoting based on context."""
        ...
```

---
