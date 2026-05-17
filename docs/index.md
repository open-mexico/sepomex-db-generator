# MexPost Data ETL Documentation

## Overview

This project builds reproducible SQLite databases from SEPOMEX postal records and GeoJSON boundaries.

## Modules

- `src.extract`: data extraction from SEPOMEX source.
- `src.transform`: schema normalization and data cleaning.
- `src.load`: relational and geospatial SQLite loading.
- `src.utils`: shared helper utilities.
- `src.main`: pipeline entry point.

## Build the docs

```bash
mkdocs build --strict
mkdocs serve
```

## API Reference

The API reference can be generated from docstrings using `mkdocstrings`.
Add dedicated pages under `docs/` as the codebase evolves.
