# Notebook Reproducibility Guide

Use this guide for any notebook added to this repository.

## Core Rules

- Keep notebooks self-contained and executable from top to bottom.
- Import all dependencies in the first code cell.
- Avoid implicit state from previous runs.
- Do not hardcode user-specific absolute paths.
- Keep runtime under control and document expensive steps.

## Recommended Structure

1. Title and objective (markdown).
2. Configuration and parameters cell.
3. Imports cell.
4. Data loading cell with explicit paths.
5. Validation cell (shape, schema, missing values).
6. Transformation and analysis cells.
7. Output/export cell.
8. Summary and next steps.

## Data Validation Checklist

Before transformation, validate at least:

- expected columns exist,
- key columns dtypes,
- null counts in critical fields,
- duplicate key rates.

## CI Validation

Notebooks can be executed in CI via:

```bash
jupyter nbconvert --execute --to notebook --inplace path/to/notebook.ipynb
```

If notebook execution is slow, mark related tests or checks as optional and document why.
