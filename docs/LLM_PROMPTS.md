# LLM Prompts for TOON Format

This document provides prompts and guidance for Large Language Models (LLMs) to understand and generate Token-Oriented Object Notation (TOON) format data.

---

## Intuitive Calling: Self-Documenting Format

TOON is a self-documenting format that uses visual markers to indicate structure:

### Square Brackets `[...]` - Arrays

Square brackets indicate arrays and their length:
- `tags[3]: reading,gaming,coding` - An array of 3 items
- `items[0]:` - An empty array
- `data[5]: 1,2,3,4,5` - A 5-element array

### Curly Braces `{...}` - Column Headings

Curly braces define column headers for tabular data (arrays of objects with identical keys):
- `items[2]{id,name}:` - Defines two columns: `id` and `name`
- Followed by data rows, one per line
- Each row contains values in the same order as headers

### Combined: Tabular Arrays

The most powerful feature combines both:

```toon
users[3]{id,name,active}:
  1,Alice,true
  2,Bob,false
  3,Carol,true
```

This immediately tells you:
- **3 users** in the array `[3]`
- **3 fields per user**: `id`, `name`, `active` `{id,name,active}`
- **Data follows** with comma-separated values

The format is intuitive because the structure is visible at a glance - square brackets count items, curly braces name columns.

---

## Lightweight Prompt

**Use this prompt when you need LLMs to understand TOON quickly and you are limited in your context window:**

````toon
TOON (Token-Oriented Object Notation) is a compact data format. Key rules:
**Objects:** `key: value` pairs, one per line, 2-space indent for nesting.
**Arrays:** Use `[length]` marker. Primitives: `tags[3]: a,b,c`. Objects with same keys: `items[2]{id,name}:\n  1,Alice\n  2,Bob` (tabular). Different keys: list format with `- ` prefix.
**Values:** Unquoted alphanumeric strings, `true`/`false`, `null`, numbers. Quote strings with special chars (`,`, `:`, `[`, `{`, `-`, spaces, or ambiguous values like `"true"`).
**No trailing spaces or final newline.**
````

---

## General Use Prompt

**Use this prompt for comprehensive TOON understanding by an LLM:**

---

````toon
# TOON Format Guide for LLMs

TOON (Token-Oriented Object Notation) is a lightweight, human-readable data serialization format optimized for token efficiency. Follow these guidelines to generate valid TOON data.

## Basic Principles

1. **Indentation:** Use 2 spaces per nesting level. Never use tabs.
2. **Line endings:** No trailing spaces on any line. Output must NOT end with a newline.
3. **Key preservation:** Maintain original key order from input data.

## Primitive Values

**Strings:**
- Alphanumeric strings and underscores: unquoted → `name: Alice`
- Quote when needed:
  - Empty strings: `""`
  - Ambiguous (looks like bool/null/number): `"true"`, `"42"`, `"null"`
  - Contains special chars (`,`, `:`, `[`, `]`, `{`, `}`, `-`): `"a,b"`, `"[test]"`
  - Leading/trailing spaces: `" padded "`
  - Control characters (escape): `"line1\\nline2"`

**Numbers:** Unquoted → `age: 30`, `price: 9.99`

**Booleans:** Lowercase, unquoted → `active: true`, `done: false`

**Null:** Unquoted → `value: null`

## Objects (Dictionaries)

Simple key-value pairs, one per line:

```toon
id: 123
name: Alice
active: true
```

Nested objects use indentation:

```toon
user:
  id: 123
  name: Alice
  settings:
    theme: dark
    notifications: true
```

Empty objects show key with colon only: `metadata:`

## Arrays

TOON has three array formats. Choose based on content:

### 1. Inline Format (Primitive Arrays)

Use for arrays of primitives (strings, numbers, booleans):

```toon
tags[3]: reading,gaming,coding
numbers[4]: 1,2,3,4
mixed[3]: Alice,42,true
```

Format: `key[length]: item1,item2,item3`

Empty arrays: `items[0]:`

**Quoting in arrays:** Quote items containing delimiter (`,`) or other special chars:
```toon
items[3]: simple,"has,comma","also:colon"
```

### 2. Tabular Format (Uniform Objects)

Use for arrays where ALL objects have IDENTICAL keys:

```toon
products[3]{id,name,price}:
  1,Widget,9.99
  2,Gadget,14.50
  3,Tool,7.25
```

Format:
- Header: `key[length]{field1,field2,field3}:`
- Data: One row per object, indented 2 spaces, comma-separated values

**Field order:** Use the key order from the first object for all rows.

**Quoting in tables:** Quote cells containing commas or special chars:
```toon
users[2]{id,name,note}:
  1,Alice,normal
  2,Bob,"needs review, urgent"
```

### 3. List Format (Non-Uniform Objects)

Use when objects have different keys OR contain nested structures:

```toon
items[3]:
  - id: 1
    name: First
  - id: 2
    name: Second
    extra: true
  - id: 3
    name: Third
    details:
      color: blue
      size: large
```

Format:
- Array declaration: `key[length]:`
- Each object starts with `- ` (hyphen + space) at base indent + 2
- Fields continue at same indent as first field

#### Choosing Array Format

**Decision tree:**
1. All primitives? → **Inline format**
2. All objects with same keys AND all values are primitives? → **Tabular format**
3. Objects with different keys OR any nested values? → **List format**

#### Complete Example

Here's a comprehensive example combining all elements:

```toon
order_id: 12345
customer: Alice_Customer
status: active
tags[2]: urgent,priority
items[3]{sku,quantity,price}:
  A001,2,9.99
  B002,1,14.50
  C003,5,3.25
shipping:
  address: "123 Main St"
  city: New York
  country: USA
metadata:
  notes[2]: "Handle with care","Fragile items"
  tracking: null
```

## Common Patterns

**Empty values:**
- Empty string: `name: ""`
- Null: `value: null`
- Empty array: `items[0]:`
- Empty object: `data:`

**Nested arrays:**
```toon
matrix[2]:
  - [3]: 1,2,3
  - [3]: 4,5,6
```

**Mixed nesting:**
```toon
users[2]:
  - id: 1
    name: Alice
    roles[2]: admin,user
  - id: 2
    name: Bob
    roles[1]: user
```

## Validation Checklist

Before returning TOON data, verify:
- ✓ 2-space indentation throughout
- ✓ No trailing spaces on lines
- ✓ No final newline at end of output
- ✓ Array lengths match actual item counts
- ✓ Tabular columns match header order
- ✓ Special characters are quoted
- ✓ Ambiguous strings are quoted
- ✓ Booleans are lowercase (`true`, `false`)

````
---

## When to Use TOON

TOON is ideal for:
- Structured data in LLM responses
- Reducing token count (60%+ vs JSON)
- Tabular data (more readable than JSON)
- Human-readable API responses
- Data science and analysis tasks

---

## Caveats

### Important Limitations and Considerations

#### No End-of-Data Markers

**Issue:** TOON format has no explicit end-of-data marker (unlike JSON's closing `}`).

**Solution:** Always wrap TOON data in code blocks when embedding in prose:

````markdown
Here is the data:
```toon
user: Alice
age: 30
```
````

or

````markdown
```
user: Alice
age: 30
```
````

This ensures clear boundaries between TOON data and surrounding text.

#### Round-Trip Ambiguities

TOON is a **lossy serialization format**. Some edge cases don't round-trip perfectly:

**Empty string vs. empty object:**
- Both encode to: `key:`
- But `key:` decodes to empty string *only*
- Empty objects cannot be reliably reconstructed as it's not known if `key:` was meant to be an empty string or an empty object

**Empty arrays are unambiguous:**
- Empty array: `items[0]:`
- Distinguishable from empty object/string

**Quoted primitives:**
- String `"true"` and boolean `true` encode differently
- But decoding always produces the most likely type

**Recommendation:** Don't rely on perfect round-trips for edge cases. TOON is designed for **forward transformation** (structured data → compact representation), not lossless bidirectional conversion.

#### Format is a Serialization and Optimization Tool

**Primary purpose:** TOON optimizes LLM interactions by:
- **Reducing tokens:** 60%+ reduction vs. JSON for tabular data
- **Reducing cognitive load:** Cleaner, more scannable structure
- **Improving readability:** Less syntax noise, clear visual hierarchy

**Not a replacement for JSON/XML in all contexts:**
- Use JSON for strict schemas and APIs requiring exact round-trips
- Use TOON for LLM prompts, responses, and token-sensitive applications

**Best practices:**
- Generate TOON for LLM consumption (prompts, context, responses)
- Parse TOON into native structures for application logic
- Don't expect byte-perfect reconstruction of edge cases

#### Type Coercion During Decoding

**Numbers:** `"42"` (quoted) and `42` (unquoted) both decode to integer `42`

**Booleans:** `"true"` (quoted) stays as string `"true"`, but `true` (unquoted) becomes boolean

**Nulls:** `"null"` (quoted) stays as string `"null"`, but `null` (unquoted) becomes `None`/`null`

**Implication:** The decoder makes intelligent guesses about types based on quoting. This is intentional for compression but means some type information is inferred, not explicit.

#### Whitespace Sensitivity

**Trailing spaces:** Forbidden. Will break parsing. Quote strings with trailing spaces if spaces are important for context.

**Indentation:** Must be exact. 2 spaces per level is standard, however consistent indent >2 spaces is acceptable as long as it's uniform.

**Final newline:** Must not exist. Output must end immediately after last character.

**Why strict?** Consistency enables reliable parsing and reduces ambiguity in a format designed for token efficiency.

#### Non-Serializable Values

Some values become `null`:
- Functions/callables: `null`
- Symbols (JavaScript): `null`
- Infinity/NaN: `null`
- Undefined: `null`

Dates/times (incl. naive) convert to ISO 8601 strings:
- `2025-01-01T00:00:00.000Z`

**Plan accordingly:** Don't expect functions or special objects to survive serialization.

#### Token Efficiency vs. JSON

**Where TOON wins:**
- Tabular data: 60-70% fewer tokens
- Nested objects: 30-50% fewer tokens
- Large arrays: 40-60% fewer tokens

**Where JSON remains competitive:**
- Very small objects (< 5 fields)
- Deeply nested structures with inconsistent shapes

**Takeaway:** TOON shines with structured, repetitive data. Use it strategically where token count matters most.

---

## Summary

TOON is a pragmatic format for LLM-optimized data serialization. It prioritizes:
- ✨ **Readability:** Self-documenting structure
- 📊 **Efficiency:** Significant token reduction
- 🎯 **Simplicity:** Intuitive visual markers

**Remember:** TOON is a compression and optimization tool, not a lossless interchange format. Use it to reduce cognitive load and token usage in LLM interactions, but be aware of its edge cases and limitations.

When generating TOON:
1. Follow the format rules strictly
2. Use appropriate array formats
3. Quote ambiguous or special values
4. Wrap output in code blocks
5. Don't expect perfect round-trips for edge cases

TOON makes your LLM prompts and responses cleaner, faster, and more efficient. Use it wisely!
