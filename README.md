# MexPost Data ETL

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![License: BSD 3-Clause](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](LICENSE)

Este repositorio proporciona un pipeline ETL que descarga el catálogo oficial de SEPOMEX,
normaliza los registros y genera dos salidas en SQLite:

- `dist/db_postal.sqlite`: base de datos relacional normalizada para busqueda postal.
- `dist/db_geo.sqlite`: base relacional con geometria GeoJSON, bounding boxes y centroides.

## 🌍 Abstract (English)

This project provides a reproducible ETL pipeline that converts SEPOMEX open postal data
and GeoJSON boundaries into production-ready SQLite databases for search and geospatial use
cases. It enforces quality through strict linting, tests with coverage thresholds, and CI
automation.

## Objetivo del Proyecto

- Mantener un dataset postal reproducible y auditable para Mexico.
- Soportar casos de uso de API y analitica (busqueda, geocodificacion, filtros espaciales).
- Asegurar calidad de ingenieria con pruebas, linting, formateo y CI.

## Estructura del Repositorio

```text
.
├── datos_geojson/            # GeoJSON polygons per state (input source)
├── dist/                     # Generated outputs (ignored by git)
├── docs/                     # Project documentation and notebook guidelines
├── scripts/                  # Utility scripts (checks and automation)
├── src/                      # ETL modules (extract, transform, load, utils, main)
├── tests/                    # Pytest test suite and fixtures
├── .pre-commit-config.yaml   # Pre-commit hooks
├── mkdocs.yml                # Documentation site configuration
├── pyproject.toml            # Project metadata + quality tool settings
├── requirements.txt          # Runtime dependencies
└── requirements-dev.txt      # Development and QA dependencies
```

## Fuentes de Datos

- SEPOMEX open data: https://www.correosdemexico.gob.mx/datosabiertos/cp/cpdescarga.txt
- GeoJSON boundaries: https://github.com/open-mexico/mexico-geojson

## Configuracion de Entorno Reproducible

### Opcion A: virtualenv (recomendada)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements-dev.txt
```

### Opcion B: conda

```bash
conda create -n mexpost python=3.11 -y
conda activate mexpost
pip install --upgrade pip
pip install -r requirements-dev.txt
```

## Ejecutar el Pipeline ETL

```bash
python -m src.main
```

Variables de entorno opcionales:

- `SEPOMEX_URL`: reemplazo de la URL de origen.
- `GEOJSON_PATH`: ruta al directorio local de GeoJSON.
- `OUTPUT_DIR`: directorio de salida para las bases generadas.

## Pruebas y Controles de Calidad

```bash
# Lint
ruff check .

# Format check
ruff format --check .

# Tests with coverage threshold
pytest
```

Comandos del task runner definidos en `pyproject.toml`:

```bash
poe check
poe fix
```

## Pre-commit

```bash
pre-commit install
pre-commit run --all-files
```

## Documentacion

Construir documentacion en local:

```bash
mkdocs build --strict
mkdocs serve
```

Paginas principales de documentacion:

- `docs/index.md`
- `docs/nb_guide.md`

## Integracion Continua

El workflow de GitHub Actions ejecuta:

- `ruff check .`
- `ruff format --check .`
- `pytest` con cobertura (`coverage.xml` se sube como artefacto)
- validacion opcional de notebooks cuando existan

## Contribuir

Consulta `CONTRIBUTING.md` antes de abrir un pull request.

## Licencia

Este proyecto esta licenciado bajo BSD 3-Clause. Ver `LICENSE`.