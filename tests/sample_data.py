"""
Sample data loader for PyToon tests.

This module provides utilities to read .toon sample files from the specification/samples/ directory.
Sample files are language-agnostic text files that contain TOON-formatted data.

This module follows the coding standards defined in docs/CODING_STANDARDS.md:
- Uses type hints throughout
- Comprehensive docstrings with examples
- Single responsibility functions
- Clear error messages
"""

from pathlib import Path
from typing import Literal

# Path to samples directory
SAMPLES_DIR = Path(__file__).parent.parent / "specification" / "samples"


def get_sample(sample_name: str) -> str:
    """
    Read the content of a .toon sample file.

    The sample name should be in the format: "category-name" where the file is
    located at specification/samples/category/category-name.toon

    Args:
        sample_name: Full sample name (e.g., "valid-simple-object-quoted-value")

    Returns:
        Raw text content of the .toon file

    Raises:
        FileNotFoundError: If the sample file does not exist or is outside samples directory

    Examples:
        >>> content = get_sample("valid-simple-object-quoted-value")
        >>> print(content)
        note: "a,b"
    """
    # Extract category from sample name
    # Format: "valid-simple-object-quoted-value" -> category: "valid-simple"
    parts = sample_name.split("-", 2)
    if len(parts) < 2:
        raise FileNotFoundError(
            f"Invalid sample name format: {sample_name}. "
            "Expected format: 'category-subcategory-name'"
        )

    # Determine category (e.g., "valid-simple", "invalid-complex")
    category = f"{parts[0]}-{parts[1]}"

    # Construct filename
    filename = f"{sample_name}.toon"

    # Build the path
    filepath = SAMPLES_DIR / category / filename

    # Resolve path and ensure it's within SAMPLES_DIR (security check)
    try:
        resolved_path = filepath.resolve()
        resolved_samples_dir = SAMPLES_DIR.resolve()

        # Check if the resolved path is under the samples directory
        if not str(resolved_path).startswith(str(resolved_samples_dir)):
            raise FileNotFoundError(
                f"Sample path is outside samples directory: {sample_name}"
            )
    except (OSError, RuntimeError) as e:
        raise FileNotFoundError(f"Invalid sample path: {sample_name}") from e

    # Check if file exists
    if not resolved_path.exists():
        raise FileNotFoundError(
            f"Sample file not found: {sample_name}\nExpected path: {filepath}"
        )

    # Read and return the content
    return resolved_path.read_text()


def list_samples(category: str) -> list[str]:
    """
    List all sample names in a category.

    Args:
        category: Category name (e.g., "valid-simple", "valid-complex")

    Returns:
        List of full sample names with prefix

    Examples:
        >>> samples = list_samples("valid-simple")
        >>> "valid-simple-integer" in samples
        True
    """
    category_dir = SAMPLES_DIR / category

    if not category_dir.exists() or not category_dir.is_dir():
        return []

    samples = []
    for filepath in category_dir.glob("*.toon"):
        # Remove .toon extension to get sample name
        sample_name = filepath.stem
        samples.append(sample_name)

    return sorted(samples)


def list_all_samples() -> list[str]:
    """
    List all available sample names across all categories.

    Returns:
        Sorted list of all sample names

    Examples:
        >>> samples = list_all_samples()
        >>> len(samples) > 0
        True
    """
    all_samples = []

    # Iterate through all subdirectories in SAMPLES_DIR
    for category_dir in SAMPLES_DIR.iterdir():
        if category_dir.is_dir() and not category_dir.name.startswith("__"):
            category_samples = list_samples(category_dir.name)
            all_samples.extend(category_samples)

    return sorted(all_samples)


def get_sample_category(sample_name: str) -> str:
    """
    Get the category for a sample name.

    Args:
        sample_name: Full sample name (e.g., "valid-simple-integer")

    Returns:
        Category name (e.g., "valid-simple")

    Examples:
        >>> get_sample_category("valid-simple-integer")
        'valid-simple'
        >>> get_sample_category("invalid-complex-trailing-space")
        'invalid-complex'
    """
    parts = sample_name.split("-", 2)
    if len(parts) < 2:
        raise ValueError(f"Invalid sample name format: {sample_name}")
    return f"{parts[0]}-{parts[1]}"


def is_valid_sample(sample_name: str) -> bool:
    """
    Check if a sample name is valid and exists.

    Args:
        sample_name: Full sample name to check

    Returns:
        True if the sample exists and is valid

    Examples:
        >>> is_valid_sample("valid-simple-integer")
        True
        >>> is_valid_sample("nonexistent-sample")
        False
    """
    try:
        get_sample(sample_name)
        return True
    except FileNotFoundError:
        return False


def get_sample_type(sample_name: str) -> Literal["valid", "invalid"]:
    """
    Get the type (valid/invalid) of a sample.

    Args:
        sample_name: Full sample name

    Returns:
        "valid" or "invalid"

    Examples:
        >>> get_sample_type("valid-simple-integer")
        'valid'
        >>> get_sample_type("invalid-simple-trailing-space")
        'invalid'
    """
    category = get_sample_category(sample_name)
    result = category.split("-")[0]
    if result not in ("valid", "invalid"):
        msg = f"Invalid sample type: {result}"
        raise ValueError(msg)
    return result  # type: ignore[return-value]
