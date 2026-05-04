import os
import pandas as pd
from datetime import datetime
import unicodedata


def limpiar_texto(texto):
    """
    Convierte a minúsculas y elimina acentos/diacríticos de un texto
    para facilitar comparaciones y búsquedas.

    No se usa `unaccent` de SQLite ya que puede requerir configuración adicional
    """
    if pd.isna(texto):
        return ""

    # Quita los acentos usando unicodedata
    texto_nfd = unicodedata.normalize("NFD", str(texto))
    # Filtra y se queda solo con los caracteres base (quita el "´")
    texto_limpio = "".join(c for c in texto_nfd if unicodedata.category(c) != "Mn")
    return texto_limpio.lower().strip()


def guardar_errores_en_archivo(codigos_no_encontrados: set, ruta_base: str = "dist"):
    """Guarda códigos postales sin geometría en un archivo de log en el directorio de salida."""
    if not codigos_no_encontrados:
        return

    os.makedirs(ruta_base, exist_ok=True)
    ruta_archivo = os.path.join(ruta_base, "db_geo_errores.log")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(ruta_archivo, "a", encoding="utf-8") as f:
        f.write(f"\n--- Ejecución: {timestamp} ---\n")
        f.write(f"Códigos postales sin geometría: {len(codigos_no_encontrados)}\n")
        for cp in sorted(codigos_no_encontrados):
            f.write(f"  {cp}\n")


def calcular_centroide(min_lon, min_lat, max_lon, max_lat):

    if min_lon is None or min_lat is None or max_lon is None or max_lat is None:
        return None, None

    centro_lat = (min_lat + max_lat) / 2.0
    centro_lon = (min_lon + max_lon) / 2.0
    return centro_lat, centro_lon
