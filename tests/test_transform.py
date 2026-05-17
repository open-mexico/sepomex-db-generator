import pandas as pd

from src.transform import normalizar_datos


def test_normalizar_datos_elimina_duplicados_y_separa_tablas():
    """Prueba que los datos crudos se separen en 3 tablas relacionales limpias."""

    # 1. Escenario: Datos con un estado y municipio DUPLICADO
    datos_simulados = {
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
    df_crudo = pd.DataFrame(datos_simulados)

    # 2. Ejecutamos
    estados, municipios, colonias = normalizar_datos(df_crudo)

    # 3. Verificamos Estados
    assert len(estados) == 1, "Debe eliminar los estados duplicados"
    assert list(estados.columns) == ["id", "nombre"]
    assert estados.iloc[0]["nombre"] == "Ciudad de México"

    # 4. Verificamos Municipios
    assert len(municipios) == 1, "Debe eliminar los municipios duplicados"
    assert list(municipios.columns) == [
        "id",
        "nombre",
        "estado_id",
        "municipio_uid",
        "nombre_normalizado",
    ]
    assert municipios.iloc[0]["estado_id"] == "09"
    assert municipios.iloc[0]["municipio_uid"] == "09-010-alvaro_obregon"

    # 5. Verificamos Colonias
    assert len(colonias) == 2, "Debe mantener todas las colonias"
    columnas_esperadas = [
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
    assert list(colonias.columns) == columnas_esperadas
    assert colonias.iloc[0]["codigo"] == "01000"
    assert colonias.iloc[0]["municipio_uid"] == "09-010-alvaro_obregon"
    assert colonias.iloc[0]["codigo_id"] == "0901000_san_angel"


def test_normalizar_datos_genera_ids_unicos_para_municipios_y_colonias():
    """Asegura que los identificadores generados no se repitan tras normalizar."""
    datos_simulados = {
        "d_codigo": ["01000", "01000", "01010"],
        "d_asenta": ["San Ángel", "San Ángel", "Los Alpes"],
        "d_tipo_asenta": ["Colonia", "Colonia", "Colonia"],
        "D_mnpio": ["Álvaro Obregón", "Alvaro Obregon", "Álvaro Obregón"],
        "d_estado": ["Ciudad de México", "Ciudad de México", "Ciudad de México"],
        "d_ciudad": ["Ciudad de México", "Ciudad de México", "Ciudad de México"],
        "c_estado": ["09", "09", "09"],
        "c_mnpio": ["010", "010", "010"],
        "d_zona": ["Urbano", "Urbano", "Urbano"],
    }
    df_crudo = pd.DataFrame(datos_simulados)

    _, municipios, colonias = normalizar_datos(df_crudo)

    assert municipios["municipio_uid"].is_unique
    assert colonias["codigo_id"].is_unique
    assert len(municipios) == 1
    assert len(colonias) == 2
