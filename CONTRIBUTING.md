# Contributing Guide

Thank you for contributing to this project.

## Development Workflow

1. Fork the repository and create a feature branch.
2. Implement your changes with tests and documentation updates.
3. Run quality checks locally before opening a pull request.
4. Open a pull request with a clear scope and rationale.

## Code Style

- Python version: 3.11+.
- Use type hints for all function signatures.
- Use Google-style docstrings for public modules and functions.
- Use `pathlib.Path` for filesystem paths.
- Use `logging` instead of `print`.
- Keep functions focused and prefer pure transformations.

## Commit Message Convention

Use Conventional Commits:

- `feat: add postal code validation utility`
- `fix: handle malformed bbox values in geo loader`
- `test: add data fixture for transform edge cases`
- `docs: update notebook reproducibility section`

## Required Checks

All pull requests must pass:

- `ruff check .`
- `ruff format --check .`
- `pytest`

Coverage threshold is enforced in CI through `pytest-cov`.

## Testing Requirements

- Every new function must have at least one corresponding test.
- Add `@pytest.mark.data` for data quality and transformation tests.
- Add `@pytest.mark.slow` for expensive end-to-end tests.
- Reuse fixtures from `tests/conftest.py` where possible.

## Documentation Requirements

- Update `README.md` when changing setup, execution, or outputs.
- Add/adjust docstrings for any modified public function.
- If notebook workflows are affected, update `docs/nb_guide.md`.

## Notebook Contribution Rules

- Notebooks must run top-to-bottom without manual state resets.
- Include explicit data loading and parameter cells.
- Keep outputs deterministic where feasible.
- Avoid hidden side effects and local absolute paths.
