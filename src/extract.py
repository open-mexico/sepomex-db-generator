"""Extraction stage for SEPOMEX source data."""

from __future__ import annotations

import logging

import pandas as pd

LOGGER = logging.getLogger(__name__)


def descargar_datos_sepomex(url: str) -> pd.DataFrame:
    """Download and parse the official SEPOMEX source file.

    Args:
        url: Public URL to the SEPOMEX source file.

    Returns:
        Raw input data as a pandas DataFrame.

    Raises:
        ValueError: If the source cannot be read or parsed.
    """
    LOGGER.info("Downloading SEPOMEX data from %s", url)
    try:
        return pd.read_csv(
            url,
            sep="|",
            encoding="ISO-8859-1",
            skiprows=[0],
            dtype={"d_codigo": "string",
                   "c_estado": "string", "c_mnpio": "string"},
        )
    except (pd.errors.EmptyDataError, pd.errors.ParserError, OSError) as error:
        raise ValueError(
            f"Could not load SEPOMEX data from '{url}': {error}") from error
