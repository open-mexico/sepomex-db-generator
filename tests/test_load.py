import json
import sqlite3

import pandas as pd

from src.load import guardar_db_geo, guardar_db_postal


def generar_datos_prueba():
    estados = pd.DataFrame({"id": ["01"], "nombre": ["Aguascalientes"]})
    municipios = pd.DataFrame(
        {"id": ["001"], "nombre": ["Aguascalientes"], "estado_id": ["01"]})

    # Creamos DOS colonias con el MISMO código postal para probar la actualización masiva
    colonias = pd.DataFrame(
        {
            "codigo": ["20049", "20049"],
            "nombre": ["Colonia Centro", "Barrio de San Marcos"],
            "tipo": ["Colonia", "Barrio"],
            "ciudad": ["Aguascalientes", "Aguascalientes"],
            "zona": ["Urbano", "Urbano"],
            "estado_id": ["01", "01"],
            "municipio_id": ["001", "001"],
        }
    )
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

        # Índices de colonias
        assert "idx_colonia_codigo" in indices
        assert "idx_colonia_nombre" in indices
        assert "idx_colonia_codigo_nombre" in indices
        assert "idx_colonia_estado_nombre" in indices
        assert "idx_colonia_estado_codigo" in indices
        assert "idx_colonia_municipio_nombre" in indices
        assert "idx_colonia_municipio_codigo" in indices

        # Índices de municipios y estados
        assert "idx_municipio_estado" in indices
        assert "idx_municipio_nombre" in indices
        assert "idx_estado_nombre" in indices


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
                # Ojo: Es un número entero en tu archivo
                "properties": {"d_codigo": 20049},
                "geometry": {"type": "Polygon", "coordinates": [[[-102.321, 21.890], [-102.325, 21.893]]]},
                "bbox": [-102.325, 21.890, -102.321, 21.893],
            }
        ],
    }

    with open(archivo_falso, "w", encoding="utf-8") as f:
        json.dump(datos_geojson, f)

    # Ejecutamos
    guardar_db_geo(estados, municipios, colonias,
                   str(ruta_db), str(ruta_geojson_dir))

    # Verificamos
    with sqlite3.connect(ruta_db) as conn:
        cursor = conn.cursor()

        # 1. Verificar índices de GeoJSON
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index';")
        indices = [fila[0] for fila in cursor.fetchall()]
        assert "idx_colonia_geo_not_null" in indices, "El índice idx_colonia_geo_not_null debe existir"
        assert "idx_colonia_bbox" in indices, "El índice idx_colonia_bbox debe existir"
        assert "idx_colonia_centro" in indices, "El índice idx_colonia_centro debe existir"
        assert "idx_colonia_estado_bbox" in indices
        assert "idx_colonia_municipio_bbox" in indices

        # 2. Verificar que AMBAS colonias con el CP 20049 recibieron la geometría
        cursor.execute(
            "SELECT nombre, geometria, min_lon, min_lat, max_lon, max_lat, centro_lon, centro_lat FROM colonias WHERE codigo = '20049'"
        )
        resultados = cursor.fetchall()

        assert len(resultados) == 2, "Deben existir dos colonias con este CP"

        for fila in resultados:
            nombre, geometria_guardada, min_lon, min_lat, max_lon, max_lat, centro_lon, centro_lat = fila
            assert geometria_guardada is not None, f"La colonia {nombre} no recibió geometría"

            geo_dict = json.loads(geometria_guardada)
            assert geo_dict["type"] == "Polygon"

            # 3. Verificar que el BBox se almacenó correctamente
            assert min_lon == -102.325, f"min_lon incorrecto para {nombre}"
            assert min_lat == 21.890, f"min_lat incorrecto para {nombre}"
            assert max_lon == -102.321, f"max_lon incorrecto para {nombre}"
            assert max_lat == 21.893, f"max_lat incorrecto para {nombre}"

            # 4. Verificar que el centroide se calculó
            assert centro_lon is not None, f"centro_lon no calculado para {nombre}"
            assert centro_lat is not None, f"centro_lat no calculado para {nombre}"
            assert abs(centro_lon - (-102.323)) < 0.001
            assert abs(centro_lat - 21.8915) < 0.001


def test_guardar_db_geo_no_pierde_bbox_si_hay_duplicados_incompletos(tmp_path):
    """Si un CP aparece repetido, conserva el payload más completo con bbox."""
    estados, municipios, colonias = generar_datos_prueba()

    ruta_db = tmp_path / "test_geo_duplicados.sqlite"
    ruta_geojson_dir = tmp_path / "datos_geojson"
    ruta_geojson_dir.mkdir()

    archivo_falso = ruta_geojson_dir / "01-Ags_test.geojson"
    datos_geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"d_codigo": 20049},
                "geometry": {"type": "Polygon", "coordinates": [[[-102.321, 21.890], [-102.325, 21.893]]]},
                "bbox": [-102.325, 21.890, -102.321, 21.893],
            },
            {
                "type": "Feature",
                "properties": {"d_codigo": 20049},
                "geometry": {"type": "Polygon", "coordinates": [[[-102.320, 21.891], [-102.324, 21.894]]]},
                # Este duplicado no trae bbox y no debe borrar datos válidos anteriores
            },
        ],
    }

    with open(archivo_falso, "w", encoding="utf-8") as f:
        json.dump(datos_geojson, f)

    guardar_db_geo(estados, municipios, colonias,
                   str(ruta_db), str(ruta_geojson_dir))

    with sqlite3.connect(ruta_db) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT min_lon, min_lat, max_lon, max_lat, centro_lon, centro_lat FROM colonias WHERE codigo = '20049'"
        )
        resultados = cursor.fetchall()

        assert len(resultados) == 2

        for min_lon, min_lat, max_lon, max_lat, centro_lon, centro_lat in resultados:
            assert min_lon == -102.325
            assert min_lat == 21.890
            assert max_lon == -102.321
            assert max_lat == 21.893
            assert centro_lon is not None
            assert centro_lat is not None


def test_guardar_db_geo_crea_log_de_errores(tmp_path):
    """Si hay CPs sin geometría, se genera un archivo de log."""
    from src.utils import guardar_errores_en_archivo

    ruta_log = tmp_path / "errores.log"
    codigos_faltantes = {"12345", "67890", "11111"}

    # Pasamos el directorio donde guardar el log
    guardar_errores_en_archivo(codigos_faltantes, str(tmp_path))

    # El archivo debe existir con el nombre correcto
    archivo_log = tmp_path / "db_geo_errores.log"
    assert archivo_log.exists()

    contenido = archivo_log.read_text(encoding="utf-8")
    assert "Códigos postales sin geometría: 3" in contenido
    assert "12345" in contenido
    assert "67890" in contenido
    assert "11111" in contenido
    assert "Ejecución:" in contenido


def test_guardar_db_geo_log_errores_en_flujo_completo(tmp_path):
    """Simula el flujo completo con CPs en DB pero sin geometría en GeoJSON."""
    estados, municipios, colonias = generar_datos_prueba()

    ruta_db = tmp_path / "test_geo_log.sqlite"
    ruta_geojson_dir = tmp_path / "datos_geojson"
    ruta_geojson_dir.mkdir()

    archivo_falso = ruta_geojson_dir / "01-Ags_test.geojson"
    datos_geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"d_codigo": 20049},
                "geometry": {"type": "Polygon", "coordinates": [[[-102.321, 21.890]]]},
                "bbox": [-102.325, 21.890, -102.321, 21.893],
            }
        ],
    }

    with open(archivo_falso, "w", encoding="utf-8") as f:
        json.dump(datos_geojson, f)

    # Agregar colonias sin geometría
    colonias_extendidas = pd.concat([
        colonias,
        pd.DataFrame({
            "codigo": ["99999", "88888"],
            "nombre": ["Colonia Ficticia", "Barrio Inexistente"],
            "tipo": ["Colonia", "Barrio"],
            "ciudad": ["Aguascalientes", "Aguascalientes"],
            "zona": ["Urbano", "Urbano"],
            "estado_id": ["01", "01"],
            "municipio_id": ["001", "001"],
        })
    ], ignore_index=True)

    guardar_db_geo(estados, municipios, colonias_extendidas,
                   str(ruta_db), str(ruta_geojson_dir))

    # El log debe existir en el mismo directorio que la BD
    ruta_output_dir = ruta_db.parent
    archivo_log_esperado = ruta_output_dir / "db_geo_errores.log"
    assert archivo_log_esperado.exists()

    contenido = archivo_log_esperado.read_text(encoding="utf-8")
    assert "99999" in contenido
    assert "88888" in contenido
    assert "Códigos postales sin geometría: 2" in contenido
