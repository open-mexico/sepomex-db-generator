"""Load stage that writes normalized data into SQLite targets."""

from __future__ import annotations

import json
import logging
import sqlite3
from pathlib import Path

import pandas as pd

from src.utils import calcular_centroide, guardar_errores_en_archivo

LOGGER = logging.getLogger(__name__)

GeoPayload = tuple[
    str,
    float | None,
    float | None,
    float | None,
    float | None,
    float | None,
    float | None,
]


def configurar_sqlite_para_carga(conn: sqlite3.Connection) -> None:
    """Apply SQLite pragmas to speed up local batch ETL loads."""
    conn.execute("PRAGMA journal_mode = OFF;")
    conn.execute("PRAGMA synchronous = OFF;")
    conn.execute("PRAGMA temp_store = MEMORY;")
    conn.execute("PRAGMA cache_size = -200000;")


def crear_indices(conn: sqlite3.Connection) -> None:
    """Create high-performance relational indexes."""
    index_statements = [
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_colonia_codigo_id ON colonias(codigo_id);",
        "CREATE INDEX IF NOT EXISTS idx_colonia_municipio_uid ON colonias(municipio_uid);",
        "CREATE INDEX IF NOT EXISTS idx_colonia_estado_codigo_id ON "
        "colonias(estado_id, codigo_id);",
        "CREATE INDEX IF NOT EXISTS idx_colonia_municipio_codigo_id ON "
        "colonias(municipio_id, codigo_id);",
        "CREATE INDEX IF NOT EXISTS idx_colonia_codigo ON colonias(codigo);",
        "CREATE INDEX IF NOT EXISTS idx_colonia_nombre ON colonias(nombre COLLATE NOCASE);",
        "CREATE INDEX IF NOT EXISTS idx_colonia_codigo_nombre ON "
        "colonias(codigo, nombre COLLATE NOCASE);",
        "CREATE INDEX IF NOT EXISTS idx_colonia_nombre_norm ON colonias(nombre_normalizado);",
        "CREATE INDEX IF NOT EXISTS idx_colonia_codigo_nombre_norm ON "
        "colonias(codigo, nombre_normalizado);",
        "CREATE INDEX IF NOT EXISTS idx_colonia_estado_nombre ON "
        "colonias(estado_id, nombre COLLATE NOCASE);",
        "CREATE INDEX IF NOT EXISTS idx_colonia_estado_nombre_norm ON "
        "colonias(estado_id, nombre_normalizado);",
        "CREATE INDEX IF NOT EXISTS idx_colonia_estado_codigo ON colonias(estado_id, codigo);",
        "CREATE INDEX IF NOT EXISTS idx_colonia_estado_codigo_nombre_norm ON "
        "colonias(estado_id, codigo, nombre_normalizado);",
        "CREATE INDEX IF NOT EXISTS idx_colonia_estado_codigo_nombre ON "
        "colonias(estado_id, codigo, nombre COLLATE NOCASE);",
        "CREATE INDEX IF NOT EXISTS idx_colonia_municipio_nombre ON "
        "colonias(municipio_id, nombre COLLATE NOCASE);",
        "CREATE INDEX IF NOT EXISTS idx_colonia_municipio_nombre_norm ON "
        "colonias(municipio_id, nombre_normalizado);",
        "CREATE INDEX IF NOT EXISTS idx_colonia_municipio_codigo ON "
        "colonias(municipio_id, codigo);",
        "CREATE INDEX IF NOT EXISTS idx_colonia_municipio_codigo_nombre_norm ON "
        "colonias(municipio_id, codigo, nombre_normalizado);",
        "CREATE INDEX IF NOT EXISTS idx_colonia_municipio_codigo_nombre ON "
        "colonias(municipio_id, codigo, nombre COLLATE NOCASE);",
        "CREATE INDEX IF NOT EXISTS idx_colonia_codigo_nombre_municipio_uid ON "
        "colonias(codigo, nombre_normalizado, municipio_uid);",
        "CREATE INDEX IF NOT EXISTS idx_municipio_estado ON municipios(estado_id);",
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_municipio_uid ON municipios(municipio_uid);",
        "CREATE INDEX IF NOT EXISTS idx_municipio_nombre ON municipios(nombre COLLATE NOCASE);",
        "CREATE INDEX IF NOT EXISTS idx_municipio_uid_nombre ON "
        "municipios(municipio_uid, nombre COLLATE NOCASE);",
        "CREATE INDEX IF NOT EXISTS idx_estado_nombre ON estados(nombre COLLATE NOCASE);",
    ]
    for statement in index_statements:
        conn.execute(statement)


def crear_vista_busqueda_colonias(
    conn: sqlite3.Connection,
    incluir_geometria: bool = False,
) -> None:
    """Create a denormalized search view for colony lookups with municipality names."""
    columnas = [
        "c.codigo_id",
        "c.codigo",
        "c.nombre AS colonia_nombre",
        "c.nombre_normalizado AS colonia_nombre_normalizado",
        "c.tipo",
        "c.ciudad",
        "c.zona",
        "c.estado_id",
        "c.municipio_id",
        "c.municipio_uid",
        "m.nombre AS municipio_nombre",
        "m.nombre_normalizado AS municipio_nombre_normalizado",
    ]
    if incluir_geometria:
        columnas.extend(
            [
                "c.geometria",
                "c.min_lon",
                "c.min_lat",
                "c.max_lon",
                "c.max_lat",
                "c.centro_lon",
                "c.centro_lat",
            ]
        )

    columnas_sql = ",\n            ".join(columnas)
    conn.execute("DROP VIEW IF EXISTS vw_colonias_busqueda")
    conn.execute(
        f"""
        CREATE VIEW vw_colonias_busqueda AS
        SELECT
            {columnas_sql}
        FROM colonias c
        LEFT JOIN municipios m
            ON c.municipio_uid = m.municipio_uid
        """
    )


def crear_indices_geo(conn: sqlite3.Connection) -> None:
    """Create indexes optimized for geospatial lookups."""
    index_statements = [
        "CREATE INDEX IF NOT EXISTS idx_colonia_geo_not_null ON "
        "colonias(codigo) WHERE geometria IS NOT NULL;",
        "CREATE INDEX IF NOT EXISTS idx_colonia_bbox ON "
        "colonias(min_lat, max_lat, min_lon, max_lon);",
        "CREATE INDEX IF NOT EXISTS idx_colonia_estado_bbox ON "
        "colonias(estado_id, min_lat, max_lat, min_lon, max_lon);",
        "CREATE INDEX IF NOT EXISTS idx_colonia_municipio_bbox ON "
        "colonias(municipio_id, min_lat, max_lat, min_lon, max_lon);",
        "CREATE INDEX IF NOT EXISTS idx_colonia_centro ON colonias(centro_lat, centro_lon);",
    ]
    for statement in index_statements:
        conn.execute(statement)


def guardar_db_postal(
    estados: pd.DataFrame,
    municipios: pd.DataFrame,
    colonias: pd.DataFrame,
    ruta_db: str | Path,
) -> None:
    """Create the lightweight relational SQLite database with indexes."""
    output_path = Path(ruta_db)
    LOGGER.info("Building relational database at %s", output_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists():
        output_path.unlink()

    with sqlite3.connect(output_path) as conn:
        configurar_sqlite_para_carga(conn)

        estados.to_sql(
            "estados",
            conn,
            if_exists="append",
            index=False,
            method="multi",
            chunksize=10_000,
        )
        municipios.to_sql(
            "municipios",
            conn,
            if_exists="append",
            index=False,
            method="multi",
            chunksize=10_000,
        )
        colonias.to_sql(
            "colonias",
            conn,
            if_exists="append",
            index=False,
            method="multi",
            chunksize=10_000,
        )

        crear_indices(conn)
        crear_vista_busqueda_colonias(conn)


def guardar_db_geo(
    estados: pd.DataFrame,
    municipios: pd.DataFrame,
    colonias: pd.DataFrame,
    ruta_db: str | Path,
    ruta_geojson: str | Path,
) -> None:
    """Create the geospatial SQLite database by injecting GeoJSON geometries by postal code."""
    output_path = Path(ruta_db)
    geojson_path = Path(ruta_geojson)
    LOGGER.info(
        "Building geospatial database at %s using GeoJSON from %s",
        output_path,
        geojson_path,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists():
        output_path.unlink()

    colonias_geo = colonias.copy()
    colonias_geo["geometria"] = None
    colonias_geo["min_lon"] = float("nan")
    colonias_geo["min_lat"] = float("nan")
    colonias_geo["max_lon"] = float("nan")
    colonias_geo["max_lat"] = float("nan")
    colonias_geo["centro_lon"] = float("nan")
    colonias_geo["centro_lat"] = float("nan")

    with sqlite3.connect(output_path) as conn:
        configurar_sqlite_para_carga(conn)

        estados.to_sql(
            "estados",
            conn,
            if_exists="append",
            index=False,
            method="multi",
            chunksize=10_000,
        )
        municipios.to_sql(
            "municipios",
            conn,
            if_exists="append",
            index=False,
            method="multi",
            chunksize=10_000,
        )
        colonias_geo.to_sql(
            "colonias",
            conn,
            if_exists="append",
            index=False,
            method="multi",
            chunksize=10_000,
        )

        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_colonia_codigo ON colonias(codigo);")

        cursor = conn.cursor()
        geojson_files = sorted(geojson_path.rglob("*.geojson"))

        total_actualizadas = 0
        codigos_no_encontrados: set[str] = set()
        actualizaciones_por_cp: dict[str, GeoPayload] = {}

        for geojson_file in geojson_files:
            with geojson_file.open("r", encoding="utf-8") as file_handle:
                data = json.load(file_handle)

            for feature in data.get("features", []):
                properties = feature.get("properties", {})
                geometry = feature.get("geometry", {})
                bbox = feature.get("bbox")

                cp_raw = properties.get("d_codigo")
                if cp_raw is None:
                    continue

                cp_str = str(cp_raw).zfill(5)
                geometry_json = json.dumps(geometry)

                min_lon: float | None = None
                min_lat: float | None = None
                max_lon: float | None = None
                max_lat: float | None = None
                centro_lon: float | None = None
                centro_lat: float | None = None

                if bbox and len(bbox) == 4:
                    min_lon, min_lat, max_lon, max_lat = bbox
                    centro_lat, centro_lon = calcular_centroide(
                        min_lon,
                        min_lat,
                        max_lon,
                        max_lat,
                    )

                new_payload: GeoPayload = (
                    geometry_json,
                    min_lon,
                    min_lat,
                    max_lon,
                    max_lat,
                    centro_lon,
                    centro_lat,
                )
                existing_payload = actualizaciones_por_cp.get(cp_str)

                if existing_payload is None:
                    actualizaciones_por_cp[cp_str] = new_payload
                    continue

                existing_bbox = existing_payload[1:5]
                new_bbox = new_payload[1:5]
                existing_has_bbox = all(
                    value is not None for value in existing_bbox)
                new_has_bbox = all(value is not None for value in new_bbox)
                if new_has_bbox and not existing_has_bbox:
                    actualizaciones_por_cp[cp_str] = new_payload

        for cp_str, payload in actualizaciones_por_cp.items():
            cursor.execute(
                """
                UPDATE colonias
                SET geometria = ?,
                    min_lon = ?, min_lat = ?, max_lon = ?, max_lat = ?,
                    centro_lon = ?, centro_lat = ?
                WHERE codigo = ?
                """,
                (*payload, cp_str),
            )

            rows_updated = cursor.rowcount
            total_actualizadas += rows_updated
            if rows_updated == 0:
                codigos_no_encontrados.add(cp_str)

        cursor.execute("SELECT DISTINCT codigo FROM colonias")
        all_postal_codes = {row[0] for row in cursor.fetchall()}
        codigos_sin_geometria = all_postal_codes - \
            set(actualizaciones_por_cp.keys())
        codigos_no_encontrados.update(codigos_sin_geometria)

        crear_indices(conn)
        crear_indices_geo(conn)
        crear_vista_busqueda_colonias(conn, incluir_geometria=True)
        conn.commit()

        LOGGER.info("Injected geometry into %d settlement rows",
                    total_actualizadas)

        if codigos_no_encontrados:
            output_dir = output_path.parent if str(
                output_path.parent) else Path("dist")
            guardar_errores_en_archivo(codigos_no_encontrados, output_dir)
            LOGGER.warning(
                "No geometry found for %d postal codes. See %s/db_geo_errores.log",
                len(codigos_no_encontrados),
                output_dir,
            )
