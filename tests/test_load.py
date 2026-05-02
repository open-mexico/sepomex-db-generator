import os
import json
import sqlite3
import pandas as pd
from src.load import guardar_db_postal, guardar_db_geo

# Fixture de datos para reutilizar en las pruebas


def generar_datos_prueba():
    estados = pd.DataFrame({'id': ['09'], 'nombre': ['Ciudad de México']})
    municipios = pd.DataFrame(
        {'id': ['010'], 'nombre': ['Álvaro Obregón'], 'estado_id': ['09']})
    colonias = pd.DataFrame({
        'codigo': ['01000'],
        'nombre': ['San Ángel'],
        'tipo': ['Colonia'],
        'ciudad': ['CDMX'],
        'zona': ['Urbano'],
        'estado_id': ['09'],
        'municipio_id': ['010']
    })
    return estados, municipios, colonias


def test_guardar_db_postal(tmp_path):
    """Prueba que la base de datos relacional se cree correctamente sin geometría."""
    estados, municipios, colonias = generar_datos_prueba()

    # Usamos tmp_path para una ruta temporal segura
    ruta_db = tmp_path / "test_postal.sqlite"

    # Ejecutamos
    guardar_db_postal(estados, municipios, colonias, str(ruta_db))

    # Verificamos
    assert os.path.exists(ruta_db), "El archivo de base de datos debe existir"

    with sqlite3.connect(ruta_db) as conn:
        cursor = conn.cursor()

        # Comprobamos que los datos están ahí
        cursor.execute("SELECT nombre FROM colonias WHERE codigo = '01000'")
        resultado = cursor.fetchone()
        assert resultado is not None
        assert resultado[0] == 'San Ángel'


def test_guardar_db_geo(tmp_path):
    """Prueba que la BD se cree y cruce exitosamente la info con un archivo GeoJSON real."""
    estados, municipios, colonias = generar_datos_prueba()

    # 1. Crear rutas temporales
    ruta_db = tmp_path / "test_geo.sqlite"
    ruta_geojson_dir = tmp_path / "datos_geojson"
    ruta_geojson_dir.mkdir()

    # 2. Fabricar un archivo GeoJSON falso dentro del directorio temporal
    archivo_falso = ruta_geojson_dir / "cdmx_test.geojson"
    datos_geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "nombre": "San Ángel",  # Mismo nombre que nuestro DataFrame
                    "cp": "01000"          # Mismo CP
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[-99.1, 19.3], [-99.2, 19.4]]]
                }
            }
        ]
    }

    with open(archivo_falso, 'w', encoding='utf-8') as f:
        json.dump(datos_geojson, f)

    # 3. Ejecutamos la carga
    guardar_db_geo(estados, municipios, colonias,
                   str(ruta_db), str(ruta_geojson_dir))

    # 4. Verificamos que se haya inyectado el polígono en la fila correcta
    with sqlite3.connect(ruta_db) as conn:
        cursor = conn.cursor()
        # Buscamos la colonia
        cursor.execute("SELECT geometria FROM colonias WHERE codigo = '01000'")
        geometria_guardada = cursor.fetchone()[0]

        assert geometria_guardada is not None, "La geometría no debe ser nula"

        # Convertimos el texto JSON de nuevo a diccionario para verificarlo
        geometria_dict = json.loads(geometria_guardada)
        assert geometria_dict["type"] == "Polygon"
