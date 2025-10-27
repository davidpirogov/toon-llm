"""
Type normalization and type guards for JSON-like values.

This module provides functions to convert arbitrary Python objects to JSON-compatible
values and type guard functions for runtime type checking.
"""

from dataclasses import asdict, is_dataclass
from datetime import datetime
from typing import Any, TypeGuard

from pytoon.types import JsonArray, JsonObject, JsonPrimitive, JsonValue


def normalize_value(value: Any, _seen: set[int] | None = None) -> JsonValue:
    """
    Normalize an arbitrary Python value to a JSON-compatible value.

    This function converts Python objects to their JSON-serializable equivalents:
    - Primitives (str, int, float, bool, None) pass through
    - Special numbers: -0 → 0, NaN/Infinity → None
    - datetime objects → ISO 8601 strings
    - lists/tuples → recursively normalized lists
    - dicts → recursively normalized dicts
    - sets → sorted lists (for deterministic output)
    - dataclasses → dicts via asdict()
    - Pydantic models → dicts via model_dump()
    - Non-serializable values → None
    - Circular references → None

    Args:
        value: Any Python object
        _seen: Internal parameter for tracking visited objects (circular reference detection)

    Returns:
        A JSON-compatible value (primitive, list, or dict)

    Examples:
        >>> normalize_value("hello")
        'hello'
        >>> normalize_value(float('nan'))
        None
        >>> normalize_value({1, 2, 3})
        [1, 2, 3]
        >>> normalize_value(datetime(2024, 1, 1))
        '2024-01-01T00:00:00'
    """
    # Initialize seen set on first call
    if _seen is None:
        _seen = set()

    # Handle None explicitly
    if value is None:
        return None

    # Primitives: str, bool (immutable, no circular reference issues)
    if isinstance(value, (str, bool)):
        return value

    # Numbers: canonicalize -0 to 0, handle NaN and Infinity
    if isinstance(value, (int, float)):
        # Check for -0
        if isinstance(value, float) and value == 0 and str(value).startswith("-"):
            return 0
        # Check for non-finite numbers (NaN, Infinity)
        if isinstance(value, float) and not (
            value == value and value != float("inf") and value != float("-inf")
        ):
            return None
        return value

    # Date/datetime → ISO string
    if isinstance(value, datetime):
        return value.isoformat()

    # Check for circular references (for mutable objects)
    obj_id = id(value)
    if obj_id in _seen:
        return None  # Circular reference detected, replace with null

    # Add to seen set for duration of normalization
    _seen.add(obj_id)

    try:
        # Lists and tuples → recursively normalized lists
        if isinstance(value, (list, tuple)):
            return [normalize_value(item, _seen) for item in value]

        # Sets → sorted list (for deterministic output)
        if isinstance(value, set):
            # Try to sort if possible, otherwise just convert to list
            try:
                return [normalize_value(item, _seen) for item in sorted(value)]
            except TypeError:
                # Items are not comparable, just convert to list
                return [normalize_value(item, _seen) for item in value]

        # Dataclasses → dict
        if is_dataclass(value) and not isinstance(value, type):
            return normalize_value(asdict(value), _seen)

        # Pydantic models → dict
        if hasattr(value, "model_dump") and callable(value.model_dump):  # type: ignore[attr-defined]
            return normalize_value(value.model_dump(), _seen)  # type: ignore[attr-defined]

        # Plain dicts → recursively normalized dicts
        if isinstance(value, dict):
            result: dict[str, JsonValue] = {}
            for key, val in value.items():
                # Convert non-string keys to strings
                str_key = str(key) if not isinstance(key, str) else key
                result[str_key] = normalize_value(val, _seen)
            return result
    finally:
        # Remove from seen set after processing
        _seen.discard(obj_id)

    # Fallback: functions, modules, classes, etc. → None
    return None


def is_json_primitive(value: Any) -> TypeGuard[JsonPrimitive]:
    """
    Check if a value is a JSON primitive.

    Args:
        value: Value to check

    Returns:
        True if value is None, str, int, float, or bool
    """
    return value is None or isinstance(value, (str, int, float, bool))


def is_json_array(value: Any) -> TypeGuard[JsonArray]:
    """
    Check if a value is a JSON array (list).

    Args:
        value: Value to check

    Returns:
        True if value is a list
    """
    return isinstance(value, list)


def is_json_object(value: Any) -> TypeGuard[JsonObject]:
    """
    Check if a value is a JSON object (dict with string keys).

    Args:
        value: Value to check

    Returns:
        True if value is a dict
    """
    return isinstance(value, dict)


def is_plain_object(value: Any) -> bool:
    """
    Check if a value is a plain dict (not a custom class instance).

    This checks that the value is a dict and not a subclass with a custom
    implementation.

    Args:
        value: Value to check

    Returns:
        True if value is exactly a dict instance
    """
    return type(value) is dict


def is_array_of_primitives(value: JsonArray) -> TypeGuard[list[JsonPrimitive]]:
    """
    Check if an array contains only primitive values.

    Args:
        value: Array to check

    Returns:
        True if all elements are primitives
    """
    return all(is_json_primitive(item) for item in value)


def is_array_of_arrays(value: JsonArray) -> TypeGuard[list[JsonArray]]:
    """
    Check if an array contains only arrays.

    Args:
        value: Array to check

    Returns:
        True if all elements are arrays
    """
    return all(is_json_array(item) for item in value)


def is_array_of_objects(value: JsonArray) -> TypeGuard[list[JsonObject]]:
    """
    Check if an array contains only objects.

    Args:
        value: Array to check

    Returns:
        True if all elements are objects
    """
    return all(is_json_object(item) for item in value)
