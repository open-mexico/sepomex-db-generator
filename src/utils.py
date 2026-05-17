"""Utility helpers for text normalization, identifiers, and geometry metadata."""

from __future__ import annotations

import unicodedata
from datetime import datetime
from pathlib import Path

import pandas as pd


def limpiar_texto(texto: object) -> str:
    """Normalize text by lowercasing and removing accents/diacritics."""
    if pd.isna(texto):
        return ""

    texto_nfd = unicodedata.normalize("NFD", str(texto))
    texto_limpio = "".join(char for char in texto_nfd if unicodedata.category(char) != "Mn")
    return texto_limpio.lower().strip()


def generar_id_codigo_postal(
    estado_id: object,
    codigo: object,
    nombre: object | None = None,
) -> str:
    """Build a stable identifier from state id, postal code, and settlement name."""
    if pd.isna(estado_id) or pd.isna(codigo):
        return ""

    estado_str = str(estado_id).strip().zfill(2)
    codigo_str = str(codigo).strip().zfill(5)

    nombre_str = _normalizar_segmento_identificador(nombre)

    base_id = f"{estado_str}{codigo_str}"
    if not nombre_str:
        return base_id

    return f"{base_id}_{nombre_str}"


def _normalizar_segmento_identificador(texto: object | None) -> str:
    """Normalize free text into a slug-like identifier segment."""
    if pd.isna(texto):
        return ""

    texto_limpio = limpiar_texto(texto)
    texto_segmentado = "".join(char if char.isalnum() else "_" for char in texto_limpio)
    return "_".join(segment for segment in texto_segmentado.split("_") if segment)


def generar_id_unico_municipio(
    estado_id: object,
    municipio_id: object,
    nombre_municipio: object | None,
) -> str:
    """Build a municipality UID using state id, municipality id, and normalized name."""
    if pd.isna(estado_id) or pd.isna(municipio_id) or pd.isna(nombre_municipio):
        return ""

    estado_str = str(estado_id).strip().zfill(2)
    municipio_str = str(municipio_id).strip().zfill(3)
    municipio_nombre_str = _normalizar_segmento_identificador(nombre_municipio)
    if not municipio_nombre_str:
        return ""

    return f"{estado_str}-{municipio_str}-{municipio_nombre_str}"


def guardar_errores_en_archivo(
    codigos_no_encontrados: set[str],
    ruta_base: str | Path = "dist",
) -> None:
    """Persist missing postal-code geometry information to a log file."""
    if not codigos_no_encontrados:
        return

    output_dir = Path(ruta_base)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "db_geo_errores.log"

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with output_file.open("a", encoding="utf-8") as file_handle:
        file_handle.write(f"\n--- Run: {timestamp} ---\n")
        file_handle.write(f"Postal codes without geometry: {len(codigos_no_encontrados)}\n")
        for postal_code in sorted(codigos_no_encontrados):
            file_handle.write(f"  {postal_code}\n")


def calcular_centroide(
    min_lon: float | None,
    min_lat: float | None,
    max_lon: float | None,
    max_lat: float | None,
) -> tuple[float | None, float | None]:
    """Compute centroid coordinates from a bounding box."""
    if min_lon is None or min_lat is None or max_lon is None or max_lat is None:
        return None, None

    centro_lat = (min_lat + max_lat) / 2.0
    centro_lon = (min_lon + max_lon) / 2.0
    return centro_lat, centro_lon
