from tests.conftest import auth, sembrar, token_de
from tests.test_espacios import administrador
from tests.test_solicitud import espacio, insertar, momento, pedir, solicitante


def test_cuatro_horas_exactas_se_aceptan(cliente):
    admin = administrador(cliente)
    sala = espacio(cliente, admin)
    token, _ = solicitante(cliente)
    respuesta = pedir(cliente, token, sala, momento(8), momento(12))
    assert respuesta.status_code == 201
    assert respuesta.json()["estado"] == "pendiente"


def test_un_minuto_sobre_cuatro_horas_se_rechaza(cliente):
    admin = administrador(cliente)
    sala = espacio(cliente, admin)
    token, _ = solicitante(cliente)
    respuesta = pedir(cliente, token, sala, momento(8), momento(12, 1))
    assert respuesta.status_code == 409
    assert respuesta.json()["codigo"] == "duracion_excedida"
    assert "cuatro horas" in respuesta.json()["mensaje"]


def test_encadenar_hasta_cuatro_horas(cliente):
    admin = administrador(cliente)
    sala = espacio(cliente, admin)
    token, _ = solicitante(cliente)
    assert pedir(cliente, token, sala, momento(8), momento(10)).status_code == 201
    respuesta = pedir(cliente, token, sala, momento(10), momento(12))
    assert respuesta.status_code == 201
    assert respuesta.json()["estado"] == "pendiente"


def test_encadenar_por_encima_de_cuatro_horas(cliente):
    admin = administrador(cliente)
    sala = espacio(cliente, admin)
    token, _ = solicitante(cliente)
    assert pedir(cliente, token, sala, momento(8), momento(10)).status_code == 201
    respuesta = pedir(cliente, token, sala, momento(10), momento(12, 1))
    assert respuesta.status_code == 409
    assert respuesta.json()["codigo"] == "duracion_excedida"


def test_un_hueco_rompe_la_consecutividad(cliente):
    admin = administrador(cliente)
    sala = espacio(cliente, admin)
    token, _ = solicitante(cliente)
    assert pedir(cliente, token, sala, momento(8), momento(10)).status_code == 201
    respuesta = pedir(cliente, token, sala, momento(10, 1), momento(14))
    assert respuesta.status_code == 201
    assert respuesta.json()["estado"] == "pendiente"


def test_otro_espacio_no_se_suma(cliente):
    admin = administrador(cliente)
    uno = espacio(cliente, admin, "LAB-01")
    dos = espacio(cliente, admin, "LAB-02")
    token, _ = solicitante(cliente)
    assert pedir(cliente, token, uno, momento(8), momento(12)).status_code == 201
    respuesta = pedir(cliente, token, dos, momento(8), momento(12))
    assert respuesta.status_code == 201
    assert respuesta.json()["espacio_id"] == dos


def test_otro_usuario_no_se_suma(cliente):
    admin = administrador(cliente)
    sala = espacio(cliente, admin)
    ana, _ = solicitante(cliente)
    assert pedir(cliente, ana, sala, momento(8), momento(12)).status_code == 201
    sembrar(cliente, "Luis", "luis@uninpahu.edu.co", "clave-luis", "solicitante")
    luis = token_de(cliente, "luis@uninpahu.edu.co", "clave-luis")
    respuesta = pedir(cliente, luis, sala, momento(12), momento(16))
    assert respuesta.status_code == 201
    assert respuesta.json()["estado"] == "pendiente"


def test_rechazada_no_alarga_el_bloque(cliente):
    admin = administrador(cliente)
    sala = espacio(cliente, admin)
    token, ana_id = solicitante(cliente)
    insertar(cliente, sala, ana_id, momento(8), momento(10), "rechazada")
    respuesta = pedir(cliente, token, sala, momento(10), momento(14))
    assert respuesta.status_code == 201
    assert respuesta.json()["estado"] == "pendiente"
