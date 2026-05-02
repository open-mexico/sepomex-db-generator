import os
import json
import sqlite3
import pandas as pd
from src.load import guardar_db_postal, guardar_db_geo


def generar_datos_prueba():
    estados = pd.DataFrame({'id': ['01'], 'nombre': ['Aguascalientes']})
    municipios = pd.DataFrame(
        {'id': ['001'], 'nombre': ['Aguascalientes'], 'estado_id': ['01']})

    # Creamos DOS colonias con el MISMO código postal para probar la actualización masiva
    colonias = pd.DataFrame({
        'codigo': ['20049', '20049'],
        'nombre': ['Colonia Centro', 'Barrio de San Marcos'],
        'tipo': ['Colonia', 'Barrio'],
        'ciudad': ['Aguascalientes', 'Aguascalientes'],
        'zona': ['Urbano', 'Urbano'],
        'estado_id': ['01', '01'],
        'municipio_id': ['001', '001']
    })
    return estados, municipios, colonias


def test_guardar_db_postal_crea_indices(tmp_path):
    """Prueba que la BD se cree y contenga los índices esperados."""
    estados, municipios, colonias = generar_datos_prueba()
    ruta_db = tmp_path / "test_postal.sqlite"

    guardar_db_postal(estados, municipios, colonias, str(ruta_db))

    with sqlite3.connect(ruta_db) as conn:
        cursor = conn.cursor()

        # Consultamos a SQLite cuáles índices existen en la base de datos
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index';")
        indices = [fila[0] for fila in cursor.fetchall()]

        # Verificamos que se hayan creado
        assert 'idx_colonia_codigo' in indices
        assert 'idx_colonia_estado_nombre' in indices
        assert 'idx_municipio_estado' in indices


def test_guardar_db_geo_actualiza_por_codigo_postal(tmp_path):
    """Prueba que el GeoJSON se inyecte usando d_codigo y afecte a todas las colonias de ese CP."""
    estados, municipios, colonias = generar_datos_prueba()

    ruta_db = tmp_path / "test_geo.sqlite"
    ruta_geojson_dir = tmp_path / "datos_geojson"
    ruta_geojson_dir.mkdir()

    # Fabricamos el GeoJSON con la estructura real que compartiste (d_codigo numérico sin padding)
    archivo_falso = ruta_geojson_dir / "01-Ags_test.geojson"
    datos_geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "d_codigo": 20049  # Ojo: Es un número entero en tu archivo
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[-102.321, 21.890], [-102.325, 21.893]]]
                }
            }
        ]
    }

    with open(archivo_falso, 'w', encoding='utf-8') as f:
        json.dump(datos_geojson, f)

    # Ejecutamos
    guardar_db_geo(estados, municipios, colonias,
                   str(ruta_db), str(ruta_geojson_dir))

    # Verificamos
    with sqlite3.connect(ruta_db) as conn:
        cursor = conn.cursor()

        # 1. Verificar índice de GeoJSON
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='index' AND name='idx_geometria_not_null';")
        assert cursor.fetchone() is not None, "El índice idx_geometria_not_null debe existir"

        # 2. Verificar que AMBAS colonias con el CP 20049 recibieron la geometría
        cursor.execute(
            "SELECT nombre, geometria FROM colonias WHERE codigo = '20049'")
        resultados = cursor.fetchall()

        assert len(resultados) == 2, "Deben existir dos colonias con este CP"

        for fila in resultados:
            geometria_guardada = fila[1]
            assert geometria_guardada is not None, f"La colonia {fila[0]} no recibió geometría"

            geo_dict = json.loads(geometria_guardada)
            assert geo_dict["type"] == "Polygon"
