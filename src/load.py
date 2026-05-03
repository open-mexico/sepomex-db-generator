import glob
import json
import os
import sqlite3

import pandas as pd

from utils import calcular_centroide


def crear_indices(conn):
    """Función auxiliar para crear todos los índices de alto rendimiento en la BD."""
    # Índices para la tabla Colonias
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_colonia_codigo ON colonias(codigo);")
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_colonia_nombre ON colonias(nombre COLLATE NOCASE);")
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_colonia_codigo_nombre ON colonias(codigo, nombre COLLATE NOCASE);")

    # Índices Compuestos (Para búsquedas filtradas por estado)
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_colonia_estado_nombre ON colonias(estado_id, nombre COLLATE NOCASE);")
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_colonia_estado_codigo ON colonias(estado_id, codigo);")

    # Índices Compuestos (Para búsquedas filtradas por municipio)
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_colonia_municipio_nombre ON colonias(municipio_id, nombre COLLATE NOCASE);")
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_colonia_municipio_codigo ON colonias(municipio_id, codigo);")

    # Índices para la tabla Municipios y Estados
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_municipio_estado ON municipios(estado_id);")
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_municipio_nombre ON municipios(nombre COLLATE NOCASE);")
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_estado_nombre ON estados(nombre COLLATE NOCASE);")


def crear_indices_geo(conn):
    """Índices específicos para la tabla Colonias con geometría."""

    # Filtro rápido para saber cuáles tienen mapa (Ej. ?solo_geo=true)
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_colonia_geo_not_null ON colonias(codigo) WHERE geometria IS NOT NULL;")

    # BBox: Para búsqueda por coordenadas (Geocodificación Inversa)
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_colonia_bbox ON colonias(min_lat, max_lat, min_lon, max_lon);")

    # Ideal si el frontend ya sabe en qué estado está el usuario y solo quiere colonias cercanas dentro de ese límite político.
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_colonia_estado_bbox ON colonias(estado_id, min_lat, max_lat, min_lon, max_lon);")

    # Extremadamente rápido si cruzamos coordenadas acotadas a un municipio en particular.
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_colonia_municipio_bbox ON colonias(municipio_id, min_lat, max_lat, min_lon, max_lon);"
    )

    # CENTROIDE: Para búsquedas de "Nearest Neighbors" (Cercanía) o clustering
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_colonia_centro ON colonias(centro_lat, centro_lon);")


def guardar_db_postal(estados: pd.DataFrame, municipios: pd.DataFrame, colonias: pd.DataFrame, ruta_db: str):
    """Crea la base de datos relacional ligera con índices."""
    print(f"💾 Creando {ruta_db}...")
    if os.path.exists(ruta_db):
        os.remove(ruta_db)

    with sqlite3.connect(ruta_db) as conn:
        estados.to_sql("estados", conn, if_exists="append", index=False)
        municipios.to_sql("municipios", conn, if_exists="append", index=False)
        colonias.to_sql("colonias", conn, if_exists="append", index=False)

        crear_indices(conn)


def guardar_db_geo(estados: pd.DataFrame, municipios: pd.DataFrame, colonias: pd.DataFrame, ruta_db: str, ruta_geojson: str):
    """Crea la base de datos geoespacial inyectando los polígonos por Código Postal."""
    print(f"🌍 Creando {ruta_db} y cruzando con GeoJSON...")
    if os.path.exists(ruta_db):
        os.remove(ruta_db)

    colonias_geo = colonias.copy()
    colonias_geo["geometria"] = None
    colonias_geo["min_lon"] = float("nan")
    colonias_geo["min_lat"] = float("nan")
    colonias_geo["max_lon"] = float("nan")
    colonias_geo["max_lat"] = float("nan")
    colonias_geo["centro_lon"] = float("nan")
    colonias_geo["centro_lat"] = float("nan")

    with sqlite3.connect(ruta_db) as conn:
        estados.to_sql("estados", conn, if_exists="append", index=False)
        municipios.to_sql("municipios", conn, if_exists="append", index=False)
        colonias_geo.to_sql("colonias", conn, if_exists="append", index=False)

        crear_indices(conn)

        # Índice exclusivo para GeoJSON (Para buscar rápido las que SÍ tienen mapa)
        crear_indices_geo(conn)

        cursor = conn.cursor()
        archivos = glob.glob(f"{ruta_geojson}/**/*.geojson", recursive=True)

        total_actualizadas = 0
        codigos_no_encontrados = set()

        for archivo in archivos:
            with open(archivo, "r", encoding="utf-8") as f:
                datos = json.load(f)
                for feature in datos.get("features", []):
                    propiedades = feature.get("properties", {})
                    geometria = feature.get("geometry", {})
                    bbox = feature.get("bbox")

                    # Extraer el código postal (se llama 'd_codigo' en tu GeoJSON)
                    cp_crudo = propiedades.get("d_codigo")

                    if cp_crudo is None:
                        continue

                    # Formatear a 5 dígitos
                    cp_str = str(cp_crudo).zfill(5)
                    geometria_json = json.dumps(geometria)

                    min_lon, min_lat, max_lon, max_lat = None, None, None, None
                    centro_lon, centro_lat = None, None

                    # Si el polígono trae BBox, extraemos los límites y calculamos el centro
                    if bbox and len(bbox) == 4:
                        min_lon, min_lat, max_lon, max_lat = bbox
                        centro_lat, centro_lon = calcular_centroide(
                            min_lon, min_lat, max_lon, max_lat)

                    # Actualizar TODAS las colonias que compartan ese Código Postal
                    cursor.execute(
                        """
                        UPDATE colonias 
                        SET geometria = ?, 
                            min_lon = ?, min_lat = ?, max_lon = ?, max_lat = ?,
                            centro_lon = ?, centro_lat = ?
                        WHERE codigo = ?
                    """,
                        (geometria_json, min_lon, min_lat, max_lon,
                         max_lat, centro_lon, centro_lat, cp_str),
                    )

                    filas_afectadas = cursor.rowcount
                    total_actualizadas += filas_afectadas

                    if filas_afectadas == 0:
                        codigos_no_encontrados.add(cp_str)

        conn.commit()
        print(f"🗺️ Se inyectó la geometría a {total_actualizadas} colonias.")

        if codigos_no_encontrados:
            print(
                f"⚠️ No se encontraron geometrías para los siguientes códigos postales: {', '.join(codigos_no_encontrados)}")
