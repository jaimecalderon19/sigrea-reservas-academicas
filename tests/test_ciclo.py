from tests.conftest import auth, sembrar, token_de
from tests.test_espacios import administrador
from tests.test_solicitud import espacio, insertar, momento, pedir, solicitante


def coordinador(cliente) -> str:
    sembrar(cliente, "Coo", "coo@uninpahu.edu.co", "clave-coo", "coordinador")
    return token_de(cliente, "coo@uninpahu.edu.co", "clave-coo")


def test_coordinador_aprueba_con_nota(cliente):
    admin = administrador(cliente)
    sala = espacio(cliente, admin)
    ana, _ = solicitante(cliente)
    reserva = pedir(cliente, ana, sala, momento(8), momento(10)).json()
    coo = coordinador(cliente)
    respuesta = cliente.post(
        f"/api/reservas/{reserva['id']}/aprobar",
        headers=auth(coo),
        json={"nota": "Hay docente asignado"},
    )
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["estado"] == "aprobada"
    assert cuerpo["nota_revision"] == "Hay docente asignado"
    assert cuerpo["revisor_id"] is not None


def test_solicitante_no_aprueba(cliente):
    admin = administrador(cliente)
    sala = espacio(cliente, admin)
    ana, _ = solicitante(cliente)
    reserva = pedir(cliente, ana, sala, momento(8), momento(10)).json()
    respuesta = cliente.post(
        f"/api/reservas/{reserva['id']}/aprobar",
        headers=auth(ana),
        json={"nota": "Yo mismo"},
    )
    assert respuesta.status_code == 403
    assert respuesta.json()["codigo"] == "prohibido"
    sigue = cliente.get("/api/reservas", headers=auth(ana)).json()
    assert sigue[0]["estado"] == "pendiente"


def test_nota_de_aprobacion_vacia(cliente):
    admin = administrador(cliente)
    sala = espacio(cliente, admin)
    ana, _ = solicitante(cliente)
    reserva = pedir(cliente, ana, sala, momento(8), momento(10)).json()
    coo = coordinador(cliente)
    respuesta = cliente.post(
        f"/api/reservas/{reserva['id']}/aprobar",
        headers=auth(coo),
        json={"nota": "  "},
    )
    assert respuesta.status_code == 400
    assert respuesta.json()["codigo"] == "datos_invalidos"
    sigue = cliente.get("/api/reservas", headers=auth(ana)).json()
    assert sigue[0]["estado"] == "pendiente"


def test_no_se_aprueba_si_no_esta_pendiente(cliente):
    admin = administrador(cliente)
    sala = espacio(cliente, admin)
    ana, ana_id = solicitante(cliente)
    reserva = pedir(cliente, ana, sala, momento(8), momento(10)).json()
    coo = coordinador(cliente)
    cliente.post(
        f"/api/reservas/{reserva['id']}/aprobar",
        headers=auth(coo),
        json={"nota": "Primera decision"},
    )
    otra = cliente.post(
        f"/api/reservas/{reserva['id']}/aprobar",
        headers=auth(coo),
        json={"nota": "Otra vez"},
    )
    assert otra.status_code == 409
    assert otra.json()["codigo"] == "estado_invalido"
    rechazada = insertar(cliente, sala, ana_id, momento(12), momento(13), "rechazada")
    respuesta = cliente.post(
        f"/api/reservas/{rechazada}/aprobar",
        headers=auth(coo),
        json={"nota": "Tarde"},
    )
    assert respuesta.status_code == 409
    assert respuesta.json()["codigo"] == "estado_invalido"


def test_rechazo_con_nota(cliente):
    admin = administrador(cliente)
    sala = espacio(cliente, admin)
    ana, _ = solicitante(cliente)
    reserva = pedir(cliente, ana, sala, momento(8), momento(10)).json()
    respuesta = cliente.post(
        f"/api/reservas/{reserva['id']}/rechazar",
        headers=auth(admin),
        json={"nota": "El laboratorio entra en mantenimiento"},
    )
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["estado"] == "rechazada"
    assert cuerpo["nota_revision"] == "El laboratorio entra en mantenimiento"
    assert cuerpo["revisor_id"] is not None


def test_el_intervalo_queda_libre_tras_el_rechazo(cliente):
    admin = administrador(cliente)
    sala = espacio(cliente, admin)
    ana, _ = solicitante(cliente)
    reserva = pedir(cliente, ana, sala, momento(8), momento(10)).json()
    cliente.post(
        f"/api/reservas/{reserva['id']}/rechazar",
        headers=auth(admin),
        json={"nota": "No procede"},
    )
    sembrar(cliente, "Luis", "luis@uninpahu.edu.co", "clave-luis", "solicitante")
    luis = token_de(cliente, "luis@uninpahu.edu.co", "clave-luis")
    respuesta = pedir(cliente, luis, sala, momento(8), momento(10))
    assert respuesta.status_code == 201
    assert respuesta.json()["estado"] == "pendiente"


def test_solicitante_cancela_la_suya_y_sigue_en_historial(cliente):
    admin = administrador(cliente)
    sala = espacio(cliente, admin)
    ana, _ = solicitante(cliente)
    reserva = pedir(cliente, ana, sala, momento(8), momento(10)).json()
    coo = coordinador(cliente)
    cliente.post(
        f"/api/reservas/{reserva['id']}/aprobar",
        headers=auth(coo),
        json={"nota": "Aprobada"},
    )
    respuesta = cliente.post(
        f"/api/reservas/{reserva['id']}/cancelar",
        headers=auth(ana),
        json={},
    )
    assert respuesta.status_code == 200
    assert respuesta.json()["estado"] == "cancelada"
    historial = cliente.get("/api/reservas", headers=auth(ana)).json()
    assert historial[0]["id"] == reserva["id"]
    assert historial[0]["estado"] == "cancelada"


def test_solicitante_no_cancela_la_de_otro(cliente):
    admin = administrador(cliente)
    sala = espacio(cliente, admin)
    ana, _ = solicitante(cliente)
    reserva = pedir(cliente, ana, sala, momento(8), momento(10)).json()
    sembrar(cliente, "Luis", "luis@uninpahu.edu.co", "clave-luis", "solicitante")
    luis = token_de(cliente, "luis@uninpahu.edu.co", "clave-luis")
    respuesta = cliente.post(
        f"/api/reservas/{reserva['id']}/cancelar",
        headers=auth(luis),
        json={},
    )
    assert respuesta.status_code == 403
    assert respuesta.json()["codigo"] == "prohibido"
    sigue = cliente.get("/api/reservas", headers=auth(ana)).json()
    assert sigue[0]["estado"] == "pendiente"


def test_administrador_cancela_una_ajena_y_libera_el_cupo(cliente):
    admin = administrador(cliente)
    sala = espacio(cliente, admin)
    ana, _ = solicitante(cliente)
    reserva = pedir(cliente, ana, sala, momento(8), momento(10)).json()
    cliente.post(
        f"/api/reservas/{reserva['id']}/aprobar",
        headers=auth(admin),
        json={"nota": "Aprobada"},
    )
    respuesta = cliente.post(
        f"/api/reservas/{reserva['id']}/cancelar",
        headers=auth(admin),
        json={"nota": "Evento institucional"},
    )
    assert respuesta.status_code == 200
    assert respuesta.json()["estado"] == "cancelada"
    ocupados = cliente.get(
        f"/api/espacios/{sala}/disponibilidad",
        headers=auth(admin),
        params={"desde": momento(7), "hasta": momento(12)},
    )
    assert ocupados.json()["ocupados"] == []


def test_no_se_cancela_una_reserva_cerrada(cliente):
    admin = administrador(cliente)
    sala = espacio(cliente, admin)
    ana, _ = solicitante(cliente)
    reserva = pedir(cliente, ana, sala, momento(8), momento(10)).json()
    coo = coordinador(cliente)
    cliente.post(
        f"/api/reservas/{reserva['id']}/rechazar",
        headers=auth(coo),
        json={"nota": "No"},
    )
    respuesta = cliente.post(
        f"/api/reservas/{reserva['id']}/cancelar",
        headers=auth(coo),
        json={},
    )
    assert respuesta.status_code == 409
    assert respuesta.json()["codigo"] == "estado_invalido"
    assert cliente.get("/api/reservas", headers=auth(ana)).json()[0]["estado"] == "rechazada"


def test_solicitante_no_ve_reservas_ajenas(cliente):
    admin = administrador(cliente)
    sala = espacio(cliente, admin)
    ana, _ = solicitante(cliente)
    mia = pedir(cliente, ana, sala, momento(8), momento(9)).json()
    sembrar(cliente, "Luis", "luis@uninpahu.edu.co", "clave-luis", "solicitante")
    luis = token_de(cliente, "luis@uninpahu.edu.co", "clave-luis")
    ajena = pedir(cliente, luis, sala, momento(9), momento(10)).json()
    vista = cliente.get("/api/reservas", headers=auth(ana)).json()
    assert [item["id"] for item in vista] == [mia["id"]]
    assert ajena["id"] not in [item["id"] for item in vista]


def test_coordinador_ve_los_cuatro_estados(cliente):
    admin = administrador(cliente)
    sala = espacio(cliente, admin)
    ana, ana_id = solicitante(cliente)
    pedir(cliente, ana, sala, momento(8), momento(9))
    aprobada = pedir(cliente, ana, sala, momento(9), momento(10)).json()
    coo = coordinador(cliente)
    cliente.post(
        f"/api/reservas/{aprobada['id']}/aprobar",
        headers=auth(coo),
        json={"nota": "Si"},
    )
    insertar(cliente, sala, ana_id, momento(11), momento(12), "rechazada")
    insertar(cliente, sala, ana_id, momento(12), momento(13), "cancelada")
    vista = cliente.get("/api/reservas", headers=auth(coo)).json()
    assert {item["estado"] for item in vista} == {
        "pendiente",
        "aprobada",
        "rechazada",
        "cancelada",
    }


def test_filtro_por_estado_cancelada(cliente):
    admin = administrador(cliente)
    sala = espacio(cliente, admin)
    ana, ana_id = solicitante(cliente)
    pedir(cliente, ana, sala, momento(8), momento(9))
    insertar(cliente, sala, ana_id, momento(10), momento(11), "cancelada")
    insertar(cliente, sala, ana_id, momento(12), momento(13), "cancelada")
    vista = cliente.get(
        "/api/reservas", headers=auth(admin), params={"estado": "cancelada"}
    ).json()
    assert vista
    assert {item["estado"] for item in vista} == {"cancelada"}
