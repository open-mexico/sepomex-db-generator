from unittest.mock import patch

import pandas as pd

from src.extract import descargar_datos_sepomex

# Usamos @patch para interceptar la llamada a pd.read_csv dentro de extract.py


@patch("src.extract.pd.read_csv")
def test_descargar_datos_sepomex_exitoso(mock_read_csv):
    """Prueba que la función intente descargar los datos con los parámetros correctos."""

    # 1. Preparamos el escenario (Mock Data)
    # Le decimos a nuestro simulador de read_csv que regrese este DataFrame falso
    df_falso = pd.DataFrame({"d_codigo": ["01000", "01010"]})
    mock_read_csv.return_value = df_falso

    # 2. Ejecutamos la función
    url_prueba = "http://url-falsa.com/datos.txt"
    resultado = descargar_datos_sepomex(url_prueba)

    # 3. Verificamos (Asserts)
    # Nos aseguramos de que read_csv fue llamado exactamente una vez con nuestra URL
    mock_read_csv.assert_called_once_with(
        url_prueba,
        sep="|",
        encoding="ISO-8859-1",
        skiprows=[0],
        dtype={"d_codigo": "string", "c_estado": "string", "c_mnpio": "string"},
    )

    # Comprobamos que nos devolvió los datos correctamente
    assert len(resultado) == 2
    assert resultado.iloc[0]["d_codigo"] == "01000"
