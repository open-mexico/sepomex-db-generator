import pandas as pd
from utils import generar_id_codigo_postal, limpiar_texto


def normalizar_datos(df_crudo: pd.DataFrame):
    """Limpia el DataFrame crudo y lo divide en Estados, Municipios y Colonias."""
    print("⚙️ Normalizando datos...")

    # Renombrar columnas clave
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

    # 1. Tabla Estados
    estados = df[["estado_id", "d_estado"]].copy()
    estados = estados.rename(columns={"estado_id": "id", "d_estado": "nombre"})
    estados = estados.drop_duplicates().sort_values(by="id")

    # 2. Tabla Municipios
    municipios = df[["municipio_id", "D_mnpio", "estado_id"]].copy()
    municipios = municipios.rename(
        columns={"municipio_id": "id", "D_mnpio": "nombre"})
    municipios = municipios.drop_duplicates().sort_values(by=[
        "estado_id", "id"])
    municipios["nombre_normalizado"] = municipios["nombre"].apply(
        limpiar_texto)

    # 3. Tabla Colonias
    columnas_colonia = ["codigo", "nombre", "tipo",
                        "ciudad", "zona", "estado_id", "municipio_id"]
    colonias = df[columnas_colonia].copy()

    colonias["codigo_id"] = colonias.apply(
        lambda fila: generar_id_codigo_postal(fila["estado_id"], fila["codigo"], fila["nombre"]), axis=1
    )
    colonias["nombre_normalizado"] = colonias["nombre"].apply(limpiar_texto)

    return estados, municipios, colonias
