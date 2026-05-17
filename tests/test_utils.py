from src.utils import calcular_centroide, generar_id_codigo_postal, limpiar_texto


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


def test_limpiar_texto_elimina_acentos():
    """Prueba que la función elimine correctamente los acentos de un texto."""
    texto_con_acentos = "Cancún, México"
    texto_limpio = limpiar_texto(texto_con_acentos)

    assert texto_limpio == "cancun, mexico"


def test_limpiar_texto_mayusculas_a_minusculas():
    """Prueba que la función convierta mayúsculas a minúsculas."""
    texto_mayusculas = "CIUDAD DE MÉXICO"
    texto_limpio = limpiar_texto(texto_mayusculas)

    assert texto_limpio == "ciudad de mexico"


def test_limpiar_texto_elimina_enes():
    """Prueba que la función elimine correctamente las eñes de un texto."""
    texto_con_ene = "Peña Nieto"
    texto_limpio = limpiar_texto(texto_con_ene)

    assert texto_limpio == "pena nieto"


def test_generar_id_codigo_postal_formato_estable():
    """El ID debe derivarse de estado + CP + nombre normalizado con padding fijo."""
    assert generar_id_codigo_postal("9", "1000", "San Ángel") == "0901000_san_angel"
    assert generar_id_codigo_postal("09", "01000", "san angel") == "0901000_san_angel"


def test_generar_id_codigo_postal_distingue_colonias_mismo_cp_y_estado():
    """Colonias distintas con mismo CP/estado deben tener IDs distintos."""
    id_1 = generar_id_codigo_postal("01", "20049", "Colonia Centro")
    id_2 = generar_id_codigo_postal("01", "20049", "Barrio de San Marcos")

    assert id_1 == "0120049_colonia_centro"
    assert id_2 == "0120049_barrio_de_san_marcos"
    assert id_1 != id_2
