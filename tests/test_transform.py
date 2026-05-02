import pandas as pd
from src.transform import normalizar_datos


def test_normalizar_datos_elimina_duplicados_y_separa_tablas():
    """Prueba que los datos crudos se separen en 3 tablas relacionales limpias."""

    # 1. Escenario: Datos con un estado y municipio DUPLICADO
    datos_simulados = {
        'd_codigo': ['01000', '01010'],
        'd_asenta': ['San Ángel', 'Los Alpes'],
        'd_tipo_asenta': ['Colonia', 'Colonia'],
        'D_mnpio': ['Álvaro Obregón', 'Álvaro Obregón'],
        'd_estado': ['Ciudad de México', 'Ciudad de México'],
        'd_ciudad': ['Ciudad de México', 'Ciudad de México'],
        'c_estado': ['09', '09'],
        'c_mnpio': ['010', '010'],
        'd_zona': ['Urbano', 'Urbano']
    }
    df_crudo = pd.DataFrame(datos_simulados)

    # 2. Ejecutamos
    estados, municipios, colonias = normalizar_datos(df_crudo)

    # 3. Verificamos Estados
    assert len(estados) == 1, "Debe eliminar los estados duplicados"
    assert list(estados.columns) == ['id', 'nombre']
    assert estados.iloc[0]['nombre'] == 'Ciudad de México'

    # 4. Verificamos Municipios
    assert len(municipios) == 1, "Debe eliminar los municipios duplicados"
    assert list(municipios.columns) == ['id', 'nombre', 'estado_id']
    assert municipios.iloc[0]['estado_id'] == '09'

    # 5. Verificamos Colonias
    assert len(colonias) == 2, "Debe mantener todas las colonias"
    columnas_esperadas = ['codigo', 'nombre', 'tipo',
                          'ciudad', 'zona', 'estado_id', 'municipio_id']
    assert list(colonias.columns) == columnas_esperadas
    assert colonias.iloc[0]['codigo'] == '01000'
