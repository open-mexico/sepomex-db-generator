"""Transformation stage that normalizes SEPOMEX data into relational tables."""

from __future__ import annotations

import logging

import pandas as pd

from src.utils import generar_id_codigo_postal, limpiar_texto

LOGGER = logging.getLogger(__name__)

REQUIRED_COLUMNS = {
    "d_codigo",
    "d_asenta",
    "d_tipo_asenta",
    "D_mnpio",
    "d_estado",
    "d_ciudad",
    "d_zona",
    "c_estado",
    "c_mnpio",
}


def _validate_required_columns(df_crudo: pd.DataFrame) -> None:
    """Validate that all required SEPOMEX columns are available."""
    missing_columns = sorted(REQUIRED_COLUMNS - set(df_crudo.columns))
    if missing_columns:
        missing_text = ", ".join(missing_columns)
        raise ValueError(
            f"Input DataFrame is missing required columns: {missing_text}")


def normalizar_datos(
    df_crudo: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Clean and split raw postal records into states, municipalities, and settlements.

    Args:
        df_crudo: Raw input table downloaded from SEPOMEX.

    Returns:
        A tuple with `(estados, municipios, colonias)` normalized tables.

    Raises:
        ValueError: If required columns are not present in the input data.
    """
    LOGGER.info("Normalizing SEPOMEX records (%d rows)", len(df_crudo))
    _validate_required_columns(df_crudo)

    df = df_crudo.rename(
        columns={
            "d_codigo": "codigo",
            "d_asenta": "nombre",
            "d_tipo_asenta": "tipo",
            "d_ciudad": "ciudad",
            "d_zona": "zona",
            "c_estado": "estado_id",
            "c_mnpio": "municipio_id",
        }
    )

    estados = df[["estado_id", "d_estado"]].copy()
    estados = estados.rename(columns={"estado_id": "id", "d_estado": "nombre"})
    estados = estados.drop_duplicates().sort_values(by="id")

    municipios = df[["municipio_id", "D_mnpio", "estado_id"]].copy()
    municipios = municipios.rename(
        columns={"municipio_id": "id", "D_mnpio": "nombre"})
    municipios = municipios.drop_duplicates().sort_values(by=[
        "estado_id", "id"])
    municipios["nombre_normalizado"] = municipios["nombre"].apply(
        limpiar_texto)

    colonias_columns = [
        "codigo",
        "nombre",
        "tipo",
        "ciudad",
        "zona",
        "estado_id",
        "municipio_id",
    ]
    colonias = df[colonias_columns].copy()
    colonias["codigo_id"] = colonias.apply(
        lambda row: generar_id_codigo_postal(
            row["estado_id"], row["codigo"], row["nombre"]),
        axis=1,
    )
    colonias["nombre_normalizado"] = colonias["nombre"].apply(limpiar_texto)

    return estados, municipios, colonias
