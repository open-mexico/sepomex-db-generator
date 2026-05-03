from src.utils import calcular_centroide


def test_calcular_centroide_valores_validos():
    """Prueba que el centroide se calcule correctamente dados cuatro límites."""
    centro_lat, centro_lon = calcular_centroide(-102.325, 21.890, -102.321, 21.893)

    assert abs(centro_lat - 21.8915) < 0.0001
    assert abs(centro_lon - (-102.323)) < 0.0001


def test_calcular_centroide_retorna_none_si_falta_valor():
    """Prueba que la función retorne (None, None) si algún parámetro es None."""
    assert calcular_centroide(None, 21.890, -102.321, 21.893) == (None, None)
    assert calcular_centroide(-102.325, None, -102.321, 21.893) == (None, None)
    assert calcular_centroide(-102.325, 21.890, None, 21.893) == (None, None)
    assert calcular_centroide(-102.325, 21.890, -102.321, None) == (None, None)
    assert calcular_centroide(None, None, None, None) == (None, None)


def test_calcular_centroide_coordenadas_simetricas():
    """Prueba el centroide de un bounding box perfecto centrado en el origen."""
    centro_lat, centro_lon = calcular_centroide(-10.0, -10.0, 10.0, 10.0)

    assert centro_lat == 0.0
    assert centro_lon == 0.0
