def calcular_centroide(min_lon, min_lat, max_lon, max_lat):

    if min_lon is None or min_lat is None or max_lon is None or max_lat is None:
        return None, None

    centro_lat = (min_lat + max_lat) / 2.0
    centro_lon = (min_lon + max_lon) / 2.0
    return centro_lat, centro_lon
