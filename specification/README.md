# Token-Oriented Object Notation Specification

## Overview

This specification defines the format for Token-Oriented Object Notation (TOON)

## Table of Contents

1. [Specification Version](#specification-version)
2. [Primitive Types](#primitive-types)
3. [Objects (Dictionaries)](#objects-dictionaries)
4. [Arrays (Lists)](#arrays-lists)
5. [Complex Structures](#complex-structures)
6. [Configuration Options](#configuration-options)
7. [Non-Serializable Values](#non-serializable-values)

---

## Specification Version

This specification is version is `0.9-beta1`.

Version 1.0 will be the first stable version of the specification. This specification can change until 1.0.

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
  869

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

- **Rule**: Keys and values separated by ": ", entries separated by newlines
- **Rule**: Key order is preserved
- **Example**:
    ```python
    {'id': 123, 'name': 'Ada', 'active': True}
    ```
    →
    ```text
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
    ```text
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
    ```text
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
    ```text
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
    ```text
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
    ```text
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
    ```text
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
    ```text
    items[2]{a,b,c}:
      1,2,3
      10,20,30
    ```

#### List Format (Different Keys)

- **Rule**: Arrays of objects with different keys use list format with "- " prefix
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
    ```text
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
    ```text
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
    ```text
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

    ```text
    items[1]:
      - nums[3]: 1,2,3
        name: test
    ```

    ```python
    {'items': [{'name': 'test', 'nums': [1, 2, 3]}]}
    ```

    →

    ```text
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
    ```text
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
    ```text
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
    ```text
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
    ```text
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
    ```text
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
    ```text
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
    ```text
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
    ```text
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
    ```text
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
    ```text
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
    ```text
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
    ```text
    [5]: x,y,"true",true,10
    ```

#### Root Tabular Arrays

- **Rule**: Root arrays of uniform objects use tabular format
- **Example**:
    ```python
    [{'id': 1}, {'id': 2}]
    ```
    →
    ```text
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
    ```text
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
    ```text
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
    ```text
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
    ```text
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
    ```text
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

#### Configuration Delimiter Purpose

- **Rule**: Allows customization of the array separator character
- **Default**: `','` (comma)
- **Supported Values**: `','`, `'|'`, `'\t'` (tab), or custom strings

#### Configuration Delimiter Primitive Arrays

- **Rule**: Delimiter is used between array elements
- **Rule**: Delimiter appears in length marker if not comma
- **Examples**:
    - Tab: `{'tags': ['reading', 'gaming', 'coding']}` with `delimiter='\t'` → `'tags[3\t]: reading\tgaming\tcoding'`
    - Pipe: `{'tags': ['reading', 'gaming', 'coding']}` with `delimiter='|'` → `'tags[3|]: reading|gaming|coding'`
    - Comma (default): `{'tags': ['reading', 'gaming', 'coding']}` → `'tags[3]: reading,gaming,coding'`

#### Configuration Delimiter Tabular Arrays

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
        ```text
        items[2	]{sku	qty	price}:
          A1	2	9.99
          B2	1	14.5
        ```
    - Pipe:
        ```text
        items[2|]{sku|qty|price}:
          A1|2|9.99
          B2|1|14.5
        ```

#### Configuration Delimiter Nested Arrays

- **Rule**: Delimiter is used consistently throughout nested structures
- **Examples**:
    - Tab: `{'pairs': [['a', 'b'], ['c', 'd']]}` with `delimiter='\t'` →
        ```text
        pairs[2	]:
          - [2	]: a	b
          - [2	]: c	d
        ```
    - Pipe: →
        ```text
        pairs[2|]:
          - [2|]: a|b
          - [2|]: c|d
        ```

#### Configuration Delimiter Root Arrays

- **Rule**: Delimiter applies to root-level arrays
- **Examples**:
    - Tab: `['x', 'y', 'z']` with `delimiter='\t'` → `'[3\t]: x\ty\tz'`
    - Pipe: `['x', 'y', 'z']` with `delimiter='|'` → `'[3|]: x|y|z'`

#### Delimiter-Aware Quoting

- **Rule**: Strings containing the active delimiter must be quoted
- **Examples**:
    - Tab delimiter: `{'items': ['a', 'b\tc', 'd']}` with `delimiter='\t'` → `'items[3\t]: a\t"b\\tc"\td'`
    - Pipe delimiter: `{'items': ['a', 'b|c', 'd']}` with `delimiter='|'` → `'items[3|]: a|"b|c"|d'`
- **Clarifications**:
    - Tabs, and other whitespace or control characters, used as delimiters should NOT be escaped when they appear in quoted strings, unless they would break the TOON format structure (newlines, carriage returns, backslashes, quotes).

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
        ```text
        items[2]{id,note}:
          1,"a,b"
          2,"c,d"
        ```
    - Tab with `delimiter='\t'`: →
        ```text
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
    ```text
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

#### Length Marker Purpose

- **Rule**: Adds an optional prefix character to array length indicators
- **Default**: `''` (no prefix)
- **Common Value**: `'#'`

#### Length Marker Primitive Arrays

- **Rule**: Marker prefixes the length number
- **Example**: `{'tags': ['reading', 'gaming', 'coding']}` with `length_marker='#'` → `'tags[#3]: reading,gaming,coding'`

#### Length Marker Empty Arrays

- **Rule**: Marker applies to empty arrays
- **Example**: `{'items': []}` with `length_marker='#'` → `'items[#0]:'`

#### Length Marker Tabular Arrays

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
    ```text
    items[#2]{sku,qty,price}:
      A1,2,9.99
      B2,1,14.5
    ```

#### Length Marker Nested Arrays

- **Rule**: Marker applies to all array levels
- **Example**: `{'pairs': [['a', 'b'], ['c', 'd']]}` with `length_marker='#'` →
    ```text
    pairs[#2]:
      - [#2]: a,b
      - [#2]: c,d
    ```

#### Combined with Delimiter

- **Rule**: Length marker can be combined with custom delimiter
- **Example**: `{'tags': ['reading', 'gaming', 'coding']}` with `length_marker='#'` and `delimiter='|'` → `'tags[#3|]: reading|gaming|coding'`

---

## Non-Serializable Values

### Arbitrary-Precision Integers

- **Rule**: Integers exceeding the standard integer range are converted to their string representation
- **Examples**:
    - TypeScript: `BigInt(123)` → `'123'`
    - Python: `123` → `'123'` (all integers are arbitrary-precision)
    - TypeScript: `{'id': BigInt(456)}` → `'id: 456'`

### Date/Time Objects

- **Rule**: Date and time objects are converted to ISO 8601 string format and quoted
- **Format**: `YYYY-MM-DDTHH:MM:SS.sssZ` (UTC recommended)
- **Rule**: Naive date/time objects (without timezone information) are assumed to be UTC
- **Examples**:
    - Python: `datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc)` → `'"2025-01-01T00:00:00.000Z"'`
    - Python: `datetime(2025, 1, 1, 0, 0, 0)` → `'"2025-01-01T00:00:00.000Z"'` (naive, assumed UTC)
    - TypeScript: `new Date('2025-01-01T00:00:00.000Z')` → `'"2025-01-01T00:00:00.000Z"'`
    - Python: `{'created': datetime(...)}` → `'created: "2025-01-01T00:00:00.000Z"'`

### Undefined/Null/None Values

- **Rule**: Language-specific null or undefined values are converted to `null`
- **Examples**:
    - Python: `None` → `'null'`
    - TypeScript: `undefined` → `'null'`
    - TypeScript: `null` → `'null'`
    - Python: `{'value': None}` → `'value: null'`
    - TypeScript: `{'value': undefined}` → `'value: null'`

### Functions and Callable Objects

- **Rule**: Functions, lambdas, methods, and other callable objects are converted to `null`
- **Examples**:
    - Python: `lambda: None` → `'null'`
    - TypeScript: `() => {}` → `'null'`
    - Python: `{'fn': lambda: None}` → `'fn: null'`
    - TypeScript: `{'fn': function() {}}` → `'fn: null'`

### Symbolic References

- **Rule**: Language-specific symbolic references or unique identifiers are converted to `null`
- **Examples**:
    - TypeScript: `Symbol('id')` → `'null'`
    - TypeScript: `{'key': Symbol('unique')}` → `'key: null'`

---

## Formatting Invariants

### No Trailing Spaces

- **Rule**: Lines must not end with trailing whitespace
- **Verification**: All output lines are checked to ensure no trailing spaces

### No Trailing Newline

- **Rule**: Output must not end with a newline character
- **Verification**: Output string must not match `/\n$/`

### Indentation

- **Rule**: Default indentation is 2 spaces per level
- **Rule**: Minimum indentation is 1 space per level (indent=0 is not supported)
- **Rule**: Any indentation level (1 space, 2 spaces, 4 spaces, tabs, etc.) may be used, but it must be consistent throughout the entire document
- **Rule**: List items use one indentation level plus "- " for first line
- **Rule**: Subsequent fields in list items align with first field (base indent + 2 additional spaces when using 2-space indent, or base indent + indent width for other levels)

### Line Separation

- **Rule**: Top-level dictionary entries are separated by newlines
- **Rule**: Array items in list format are separated by newlines
- **Rule**: Tabular array rows each on separate line with one indentation level
