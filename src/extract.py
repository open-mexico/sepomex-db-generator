import pandas as pd


def descargar_datos_sepomex(url: str) -> pd.DataFrame:
    """Descarga y lee el archivo oficial de SEPOMEX."""
    print(f"⏳ Descargando datos desde: {url}")
    df_crudo = pd.read_csv(
        url,
        sep="|",
        encoding="ISO-8859-1",
        skiprows=[0],
        dtype={'d_codigo': 'string', 'c_estado': 'string', 'c_mnpio': 'string'}
    )
    return df_crudo
