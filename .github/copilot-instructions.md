# Copilot Instructions for This Repository

## Core Engineering Standards

- Use Python 3.11+ with strict typing and docstrings (Google style).
- Prefer pure functions for data transformations; avoid side effects and global state.
- All paths should be configurable, never hardcoded (use pathlib.Path).
- Notebooks must be self-contained and runnable from top to bottom; avoid implicit state.
- Always validate input data (shape, dtypes, missing values) before processing.
- Use pandas (or Polars) with method chaining and avoid in-place modifications unless explicitly needed.
- Log progress using the `logging` module, not `print`.
- Every new function must have a corresponding test.
- For data loading, include error handling for missing files and corrupt data.
- Prefer `ruff` for formatting and linting; code must pass `ruff check` and `ruff format --check` before committing.

## Testing and Data Quality

- Add `@pytest.mark.data` to tests focused on schema or cleaning logic.
- Add `@pytest.mark.slow` to tests that execute heavy ETL or notebook runs.
- Use fixtures from `tests/conftest.py` whenever possible.
- Validate expected columns and key nullability constraints in tests.

## Documentation

- Keep module-level and function-level docstrings in English.
- Update `README.md` and relevant docs when behavior changes.
- Add short rationale comments only where the code is non-obvious.
