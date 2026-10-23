from sigrea.dominio.claves import hash_clave, normalizar_correo, verificar_clave


def test_el_mismo_correo_en_mayusculas_normaliza_igual():
    assert normalizar_correo("Admin@Uninpahu.edu.co") == normalizar_correo(
        "admin@uninpahu.edu.co"
    )


def test_la_clave_no_se_guarda_en_claro():
    guardada = hash_clave("clave-secreta")
    assert "clave-secreta" not in guardada
    assert verificar_clave("clave-secreta", guardada)
    assert not verificar_clave("otra", guardada)
