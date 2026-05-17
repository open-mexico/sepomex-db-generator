"""Data processing tests for transformation behavior."""

from __future__ import annotations

import pandas as pd
import pytest

from src.transform import normalizar_datos


@pytest.mark.data
def test_normalizar_datos_generates_expected_relational_tables(
    sample_raw_postal_df: pd.DataFrame,
) -> None:
    """Validate that normalization returns expected table structure and deterministic ids."""
    estados, municipios, colonias = normalizar_datos(sample_raw_postal_df)

    assert list(estados.columns) == ["id", "nombre"]
    assert len(estados) == 1
    assert estados.iloc[0]["id"] == "09"

    assert list(municipios.columns) == [
        "id",
        "nombre",
        "estado_id",
        "municipio_uid",
        "nombre_normalizado",
    ]
    assert len(municipios) == 1
    assert municipios.iloc[0]["municipio_uid"] == "09-010-alvaro_obregon"
    assert municipios.iloc[0]["nombre_normalizado"] == "alvaro obregon"

    assert list(colonias.columns) == [
        "codigo",
        "nombre",
        "tipo",
        "ciudad",
        "zona",
        "estado_id",
        "municipio_id",
        "municipio_uid",
        "codigo_id",
        "nombre_normalizado",
    ]
    assert len(colonias) == 2
    assert colonias.iloc[0]["municipio_uid"] == "09-010-alvaro_obregon"
    assert colonias.iloc[0]["codigo_id"] == "0901000_san_angel"
