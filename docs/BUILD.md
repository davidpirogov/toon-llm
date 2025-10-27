# Build

Building py-toon can be done with python:

```bash
uv run pytest tests/
tox
uv build
```

The distribution-ready files will be in the `dist/` directory.

## Packaging and Distribution

Packaging after changes need the following to be executed:

### Update the version number

Bump the version number (the `__version__` variable in `pytoon/__init__.py` is automatically read from `pyproject.toml`):

- The MAJOR and MINOR versions should **always** have an associated reviewed pull request
- The PATCH version should be bumped for small changes, documentation updates, and minor fixes

```bash
uv lock
uv version --dry-run --bump patch
uv version --bump patch
git add pyproject.toml uv.lock
git commit -m "Bump version to $(uv version | awk '{print $2}')"
git tag "v$(uv version | awk '{print $2}')"
git push && git push --tags
```

### Distribute

```bash
uv build && uv publish && rm -rf dist
```

Remember to set the `username` to `__token__` and the `password` to your PyPI token.
