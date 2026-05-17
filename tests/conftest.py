"""Shared pytest fixtures for data-processing tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture
def sample_raw_postal_df() -> pd.DataFrame:
    """Return a small SEPOMEX-like DataFrame used across tests."""
    return pd.DataFrame(
        {
            "d_codigo": ["01000", "01010"],
            "d_asenta": ["San Ángel", "Los Alpes"],
            "d_tipo_asenta": ["Colonia", "Colonia"],
            "D_mnpio": ["Álvaro Obregón", "Álvaro Obregón"],
            "d_estado": ["Ciudad de México", "Ciudad de México"],
            "d_ciudad": ["Ciudad de México", "Ciudad de México"],
            "c_estado": ["09", "09"],
            "c_mnpio": ["010", "010"],
            "d_zona": ["Urbano", "Urbano"],
        }
    )


@pytest.fixture
def temporary_output_dir(tmp_path_factory: pytest.TempPathFactory) -> str:
    """Create and return a temporary output directory path as string."""
    return str(tmp_path_factory.mktemp("outputs"))
