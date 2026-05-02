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
    """Crea la base de datos geoespacial inyectando los polígonos por Código Postal."""
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
        codigos_no_encontrados = set()

        for archivo in archivos:
            with open(archivo, 'r', encoding='utf-8') as f:
                datos = json.load(f)
                for feature in datos.get('features', []):
                    propiedades = feature.get('properties', {})
                    geometria = feature.get('geometry', {})

                    # 1. Extraer el código postal (se llama 'd_codigo' en el GeoJSON)
                    cp_crudo = propiedades.get('d_codigo')

                    if cp_crudo is None:
                        continue  # Saltamos si no hay código

                    # 2. Formatear el CP a string de 5 dígitos (ej. 20049 -> "20049", 1000 -> "01000")
                    cp_str = str(cp_crudo).zfill(5)

                    geometria_json = json.dumps(geometria)

                    # 3. Actualizar TODAS las colonias que compartan ese Código Postal
                    cursor.execute("""
                        UPDATE colonias 
                        SET geometria = ? 
                        WHERE codigo = ?
                    """, (geometria_json, cp_str))

                    filas_afectadas = cursor.rowcount
                    total_actualizadas += filas_afectadas

                    # Opcional: Registrar si un CP del mapa no existe en SEPOMEX
                    if filas_afectadas == 0:
                        codigos_no_encontrados.add(cp_str)

        conn.commit()
        print(f"🗺️ Se inyectó la geometría a {total_actualizadas} colonias.")
        if codigos_no_encontrados:
            print(
                f"⚠️ Nota: {len(codigos_no_encontrados)} códigos del mapa no se encontraron en SEPOMEX.")
