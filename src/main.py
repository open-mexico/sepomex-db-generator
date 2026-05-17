"""Main ETL entry point for generating relational and geospatial SQLite databases."""

from __future__ import annotations

import logging
import os
from pathlib import Path

from src.extract import descargar_datos_sepomex
from src.load import guardar_db_geo, guardar_db_postal
from src.transform import normalizar_datos

DEFAULT_SEPOMEX_URL = "https://www.correosdemexico.gob.mx/datosabiertos/cp/cpdescarga.txt"


def _configure_logging() -> None:
    """Configure baseline logging for CLI execution."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def main() -> None:
    """Run the ETL pipeline end-to-end."""
    _configure_logging()

    sepomex_url = os.getenv("SEPOMEX_URL", DEFAULT_SEPOMEX_URL)
    geojson_path = Path(os.getenv("GEOJSON_PATH", "datos_geojson"))
    output_dir = Path(os.getenv("OUTPUT_DIR", "dist"))

    logging.info("Starting ETL pipeline")
    df_crudo = descargar_datos_sepomex(sepomex_url)
    estados, municipios, colonias = normalizar_datos(df_crudo)

    guardar_db_postal(estados, municipios, colonias, output_dir / "db_postal.sqlite")
    guardar_db_geo(estados, municipios, colonias, output_dir / "db_geo.sqlite", geojson_path)
    logging.info("Databases generated successfully in %s", output_dir)


if __name__ == "__main__":
    main()
