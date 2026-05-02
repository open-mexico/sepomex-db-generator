from extract import descargar_datos_sepomex
from transform import normalizar_datos
from load import guardar_db_postal, guardar_db_geo


def main():
    URL_SEPOMEX = 'https://www.correosdemexico.gob.mx/datosabiertos/cp/cpdescarga.txt'
    RUTA_GEOJSON = 'datos_geojson'

    # 1. Extraer
    df_crudo = descargar_datos_sepomex(URL_SEPOMEX)

    # 2. Transformar
    estados, municipios, colonias = normalizar_datos(df_crudo)

    # 3. Cargar
    guardar_db_postal(estados, municipios, colonias, 'db_postal.sqlite')
    guardar_db_geo(estados, municipios, colonias,
                   'db_geo.sqlite', RUTA_GEOJSON)

    print("✅ ¡Bases de datos generadas exitosamente!")


if __name__ == '__main__':
    main()
