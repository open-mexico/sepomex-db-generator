import os
import glob
import json
import sqlite3
import pandas as pd


def guardar_db_postal(estados: pd.DataFrame, municipios: pd.DataFrame, colonias: pd.DataFrame, ruta_db: str):
    """Crea la base de datos relacional ligera."""
    print(f"💾 Creando {ruta_db}...")
    if os.path.exists(ruta_db):
        os.remove(ruta_db)

    with sqlite3.connect(ruta_db) as conn:
        estados.to_sql('estados', conn, if_exists='append', index=False)
        municipios.to_sql('municipios', conn, if_exists='append', index=False)
        colonias.to_sql('colonias', conn, if_exists='append', index=False)

        conn.execute("CREATE INDEX idx_colonia_nombre ON colonias(nombre);")
        conn.execute("CREATE INDEX idx_colonia_codigo ON colonias(codigo);")


def guardar_db_geo(estados: pd.DataFrame, municipios: pd.DataFrame, colonias: pd.DataFrame, ruta_db: str, ruta_geojson: str):
    """Crea la base de datos geoespacial inyectando los polígonos."""
    print(f"🌍 Creando {ruta_db} y cruzando con GeoJSON...")
    if os.path.exists(ruta_db):
        os.remove(ruta_db)

    colonias_geo = colonias.copy()
    colonias_geo['geometria'] = None

    with sqlite3.connect(ruta_db) as conn:
        estados.to_sql('estados', conn, if_exists='append', index=False)
        municipios.to_sql('municipios', conn, if_exists='append', index=False)
        colonias_geo.to_sql('colonias', conn, if_exists='append', index=False)

        conn.execute(
            "CREATE INDEX idx_colonia_nombre_geo ON colonias(nombre);")
        conn.execute(
            "CREATE INDEX idx_colonia_codigo_geo ON colonias(codigo);")

        cursor = conn.cursor()
        archivos = glob.glob(f'{ruta_geojson}/**/*.geojson', recursive=True)

        total_actualizadas = 0
        for archivo in archivos:
            with open(archivo, 'r', encoding='utf-8') as f:
                datos = json.load(f)
                for feature in datos.get('features', []):
                    propiedades = feature.get('properties', {})
                    geometria = feature.get('geometry', {})

                    nombre = str(propiedades.get('nombre', '')).upper()
                    cp = str(propiedades.get('cp', ''))

                    cursor.execute("""
                        UPDATE colonias 
                        SET geometria = ? 
                        WHERE codigo = ? AND UPPER(nombre) = ?
                    """, (json.dumps(geometria), cp, nombre))
                    total_actualizadas += cursor.rowcount

        print(f"🗺️ Se inyectaron {total_actualizadas} polígonos.")
