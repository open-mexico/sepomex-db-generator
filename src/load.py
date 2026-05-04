import glob
import json
import os
import sqlite3

import pandas as pd

from utils import calcular_centroide, guardar_errores_en_archivo


def configurar_sqlite_para_carga(conn: sqlite3.Connection):
    """Ajustes seguros para acelerar cargas batch en procesos ETL locales."""
    conn.execute("PRAGMA journal_mode = OFF;")
    conn.execute("PRAGMA synchronous = OFF;")
    conn.execute("PRAGMA temp_store = MEMORY;")
    conn.execute("PRAGMA cache_size = -200000;")


def crear_indices(conn):
    """Función auxiliar para crear todos los índices de alto rendimiento en la BD."""
    # Índices para la tabla Colonias
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_colonia_codigo ON colonias(codigo);")
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_colonia_nombre ON colonias(nombre COLLATE NOCASE);")
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_colonia_codigo_nombre ON colonias(codigo, nombre COLLATE NOCASE);")

    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_colonia_nombre_norm ON colonias(nombre_normalizado);")
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_colonia_codigo_nombre_norm ON colonias(codigo, nombre_normalizado);")

    # Índices Compuestos (Para búsquedas filtradas por estado)
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_colonia_estado_nombre ON colonias(estado_id, nombre COLLATE NOCASE);")
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_colonia_estado_nombre_norm ON colonias(estado_id, nombre_normalizado);")
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_colonia_estado_codigo ON colonias(estado_id, codigo);")

    # Índices Compuestos (Para búsquedas filtradas por municipio)
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_colonia_municipio_nombre ON colonias(municipio_id, nombre COLLATE NOCASE);")
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_colonia_municipio_nombre_norm ON colonias(municipio_id, nombre_normalizado);")
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
    dir_salida = os.path.dirname(ruta_db)
    if dir_salida:
        os.makedirs(dir_salida, exist_ok=True)
    if os.path.exists(ruta_db):
        os.remove(ruta_db)

    with sqlite3.connect(ruta_db) as conn:
        configurar_sqlite_para_carga(conn)

        estados.to_sql("estados", conn, if_exists="append",
                       index=False, method="multi", chunksize=10_000)
        municipios.to_sql("municipios", conn, if_exists="append",
                          index=False, method="multi", chunksize=10_000)
        colonias.to_sql("colonias", conn, if_exists="append",
                        index=False, method="multi", chunksize=10_000)

        crear_indices(conn)


def guardar_db_geo(estados: pd.DataFrame, municipios: pd.DataFrame, colonias: pd.DataFrame, ruta_db: str, ruta_geojson: str):
    """Crea la base de datos geoespacial inyectando los polígonos por Código Postal."""
    print(f"🌍 Creando {ruta_db} y cruzando con GeoJSON...")
    dir_salida = os.path.dirname(ruta_db)
    if dir_salida:
        os.makedirs(dir_salida, exist_ok=True)
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
        configurar_sqlite_para_carga(conn)

        estados.to_sql("estados", conn, if_exists="append",
                       index=False, method="multi", chunksize=10_000)
        municipios.to_sql("municipios", conn, if_exists="append",
                          index=False, method="multi", chunksize=10_000)
        colonias_geo.to_sql("colonias", conn, if_exists="append",
                            index=False, method="multi", chunksize=10_000)

        # Para la fase de UPDATE solo necesitamos el índice por código postal.
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_colonia_codigo ON colonias(codigo);")

        cursor = conn.cursor()
        archivos = sorted(
            glob.glob(f"{ruta_geojson}/**/*.geojson", recursive=True))

        total_actualizadas = 0
        codigos_no_encontrados = set()
        actualizaciones_por_cp = {}

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

                    nuevo_payload = (
                        geometria_json,
                        min_lon,
                        min_lat,
                        max_lon,
                        max_lat,
                        centro_lon,
                        centro_lat,
                    )
                    payload_existente = actualizaciones_por_cp.get(cp_str)

                    if payload_existente is None:
                        actualizaciones_por_cp[cp_str] = nuevo_payload
                    else:
                        # Conservamos el payload más completo (con BBox/centroide)
                        bbox_existente = payload_existente[1:5]
                        bbox_nuevo = nuevo_payload[1:5]
                        existente_tiene_bbox = all(
                            v is not None for v in bbox_existente)
                        nuevo_tiene_bbox = all(
                            v is not None for v in bbox_nuevo)

                        if nuevo_tiene_bbox and not existente_tiene_bbox:
                            actualizaciones_por_cp[cp_str] = nuevo_payload

        # Ejecutamos solo una actualización por CP para evitar reescrituras repetidas.
        for cp_str, payload in actualizaciones_por_cp.items():
            cursor.execute(
                """
                UPDATE colonias
                SET geometria = ?,
                    min_lon = ?, min_lat = ?, max_lon = ?, max_lat = ?,
                    centro_lon = ?, centro_lat = ?
                WHERE codigo = ?
            """,
                (*payload, cp_str),
            )

            filas_afectadas = cursor.rowcount
            total_actualizadas += filas_afectadas

            if filas_afectadas == 0:
                codigos_no_encontrados.add(cp_str)

        # Identificar CPs en la BD que nunca aparecieron en el GeoJSON
        cursor.execute("SELECT DISTINCT codigo FROM colonias")
        todos_codigos_bd = {fila[0] for fila in cursor.fetchall()}
        codigos_sin_geometria = todos_codigos_bd - \
            set(actualizaciones_por_cp.keys())
        codigos_no_encontrados.update(codigos_sin_geometria)

        # Creamos el resto de índices al final para acelerar la carga inicial.
        crear_indices(conn)
        crear_indices_geo(conn)

        conn.commit()
        print(f"🗺️ Se inyectó la geometría a {total_actualizadas} colonias.")

        if codigos_no_encontrados:
            ruta_output_dir = os.path.dirname(ruta_db) or "dist"
            guardar_errores_en_archivo(codigos_no_encontrados, ruta_output_dir)
            print(
                f"⚠️ No se encontraron geometrías para {len(codigos_no_encontrados)} códigos postales. Ver: {ruta_output_dir}/db_geo_errores.log")
