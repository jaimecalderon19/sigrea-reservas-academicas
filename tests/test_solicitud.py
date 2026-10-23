from datetime import datetime, timezone

from tests.conftest import auth, sembrar, token_de
from tests.test_espacios import administrador, crear


def momento(hora, minuto=0, segundo=0) -> str:
    return f"2026-10-26T{hora:02d}:{minuto:02d}:{segundo:02d}-05:00"


def solicitante(cliente, correo="ana@uninpahu.edu.co", clave="clave-ana"):
    sembrar(cliente, "Ana Ruiz", correo, clave, "solicitante")
    token = token_de(cliente, correo, clave)
    yo = cliente.get("/api/usuarios/yo", headers=auth(token)).json()
    return token, yo["id"]


def espacio(cliente, token_admin, codigo="LAB-01"):
    respuesta = crear(cliente, token_admin, codigo=codigo, nombre=codigo)
    assert respuesta.status_code == 201, respuesta.text
    return respuesta.json()["id"]


def pedir(cliente, token, espacio_id, inicio, fin, proposito="Clase de redes"):
    return cliente.post(
        "/api/reservas",
        headers=auth(token),
        json={
            "espacio_id": espacio_id,
            "inicio": inicio,
            "fin": fin,
            "proposito": proposito,
        },
    )


def insertar(cliente, espacio_id, solicitante_id, inicio, fin, estado):
    from sigrea.infraestructura.modelos import Reserva

    db = cliente.app.state.fabrica()
    try:
        fila = Reserva(
            espacio_id=espacio_id,
            solicitante_id=solicitante_id,
            inicio=datetime.fromisoformat(inicio).astimezone(timezone.utc),
            fin=datetime.fromisoformat(fin).astimezone(timezone.utc),
            proposito="Carga de prueba",
            estado=estado,
            creado_en=datetime.now(timezone.utc),
        )
        db.add(fila)
        db.commit()
        return fila.id
    finally:
        db.close()


def test_solicitud_aceptada_queda_pendiente_a_su_nombre(cliente):
    admin = administrador(cliente)
    sala = espacio(cliente, admin)
    token, ana = solicitante(cliente)
    respuesta = pedir(cliente, token, sala, momento(8), momento(10))
    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["estado"] == "pendiente"
    assert cuerpo["solicitante_id"] == ana
    assert cuerpo["proposito"] == "Clase de redes"


def test_proposito_vacio(cliente):
    admin = administrador(cliente)
    sala = espacio(cliente, admin)
    token, _ = solicitante(cliente)
    respuesta = pedir(cliente, token, sala, momento(8), momento(10), "   ")
    assert respuesta.status_code == 400
    assert respuesta.json()["codigo"] == "datos_invalidos"


def test_proposito_de_501_caracteres(cliente):
    admin = administrador(cliente)
    sala = espacio(cliente, admin)
    token, _ = solicitante(cliente)
    respuesta = pedir(cliente, token, sala, momento(8), momento(10), "a" * 501)
    assert respuesta.status_code == 400
    assert respuesta.json()["codigo"] == "datos_invalidos"


def test_espacio_inactivo(cliente):
    admin = administrador(cliente)
    sala = espacio(cliente, admin)
    cliente.patch(f"/api/espacios/{sala}", headers=auth(admin), json={"activo": False})
    token, _ = solicitante(cliente)
    respuesta = pedir(cliente, token, sala, momento(8), momento(10))
    assert respuesta.status_code == 409
    assert respuesta.json()["codigo"] == "espacio_inactivo"


def test_espacio_inexistente(cliente):
    token, _ = solicitante(cliente)
    respuesta = pedir(cliente, token, 999, momento(8), momento(10))
    assert respuesta.status_code == 404
    assert respuesta.json()["codigo"] == "no_encontrado"


def test_coordinador_no_crea_solicitudes(cliente):
    admin = administrador(cliente)
    sala = espacio(cliente, admin)
    sembrar(cliente, "Coo", "coo@uninpahu.edu.co", "clave-coo", "coordinador")
    token = token_de(cliente, "coo@uninpahu.edu.co", "clave-coo")
    respuesta = pedir(cliente, token, sala, momento(8), momento(10))
    assert respuesta.status_code == 403
    assert respuesta.json()["codigo"] == "prohibido"


def test_fin_no_posterior(cliente):
    admin = administrador(cliente)
    sala = espacio(cliente, admin)
    token, _ = solicitante(cliente)
    respuesta = pedir(cliente, token, sala, momento(10), momento(10))
    assert respuesta.status_code == 400
    assert respuesta.json()["codigo"] == "datos_invalidos"


def test_duracion_de_29_minutos(cliente):
    admin = administrador(cliente)
    sala = espacio(cliente, admin)
    token, _ = solicitante(cliente)
    respuesta = pedir(cliente, token, sala, momento(8), momento(8, 29))
    assert respuesta.status_code == 400
    assert respuesta.json()["codigo"] == "datos_invalidos"


def test_duracion_de_30_minutos(cliente):
    admin = administrador(cliente)
    sala = espacio(cliente, admin)
    token, _ = solicitante(cliente)
    respuesta = pedir(cliente, token, sala, momento(8), momento(8, 30))
    assert respuesta.status_code == 201
    assert respuesta.json()["estado"] == "pendiente"


def test_instante_sin_zona(cliente):
    admin = administrador(cliente)
    sala = espacio(cliente, admin)
    token, _ = solicitante(cliente)
    respuesta = pedir(
        cliente,
        token,
        sala,
        "2026-10-26T08:00:00",
        "2026-10-26T10:00:00",
    )
    assert respuesta.status_code == 400
    assert respuesta.json()["codigo"] == "datos_invalidos"


def test_jornada_de_diez_horas_supera_el_tope(cliente):
    admin = administrador(cliente)
    sala = espacio(cliente, admin)
    token, _ = solicitante(cliente)
    respuesta = pedir(cliente, token, sala, momento(8), momento(18))
    assert respuesta.status_code == 409
    assert respuesta.json()["codigo"] == "duracion_excedida"


def test_solape_con_pendiente(cliente):
    admin = administrador(cliente)
    sala = espacio(cliente, admin)
    ana, _ = solicitante(cliente)
    assert pedir(cliente, ana, sala, momento(8), momento(10)).status_code == 201
    sembrar(cliente, "Luis", "luis@uninpahu.edu.co", "clave-luis", "solicitante")
    luis = token_de(cliente, "luis@uninpahu.edu.co", "clave-luis")
    respuesta = pedir(cliente, luis, sala, momento(9), momento(11))
    assert respuesta.status_code == 409
    assert respuesta.json()["codigo"] == "espacio_no_disponible"


def test_solape_con_aprobada(cliente):
    admin = administrador(cliente)
    sala = espacio(cliente, admin)
    _, ana = solicitante(cliente)
    insertar(cliente, sala, ana, momento(8), momento(10), "aprobada")
    sembrar(cliente, "Luis", "luis@uninpahu.edu.co", "clave-luis", "solicitante")
    luis = token_de(cliente, "luis@uninpahu.edu.co", "clave-luis")
    respuesta = pedir(cliente, luis, sala, momento(9), momento(11))
    assert respuesta.status_code == 409
    assert respuesta.json()["codigo"] == "espacio_no_disponible"


def test_intervalo_identico_a_una_pendiente(cliente):
    admin = administrador(cliente)
    sala = espacio(cliente, admin)
    ana, _ = solicitante(cliente)
    assert pedir(cliente, ana, sala, momento(8), momento(10)).status_code == 201
    sembrar(cliente, "Luis", "luis@uninpahu.edu.co", "clave-luis", "solicitante")
    luis = token_de(cliente, "luis@uninpahu.edu.co", "clave-luis")
    respuesta = pedir(cliente, luis, sala, momento(8), momento(10))
    assert respuesta.status_code == 409
    assert respuesta.json()["codigo"] == "espacio_no_disponible"


def test_mismo_intervalo_en_otro_espacio(cliente):
    admin = administrador(cliente)
    uno = espacio(cliente, admin, "LAB-01")
    dos = espacio(cliente, admin, "LAB-02")
    ana, _ = solicitante(cliente)
    assert pedir(cliente, ana, uno, momento(8), momento(10)).status_code == 201
    sembrar(cliente, "Luis", "luis@uninpahu.edu.co", "clave-luis", "solicitante")
    luis = token_de(cliente, "luis@uninpahu.edu.co", "clave-luis")
    respuesta = pedir(cliente, luis, dos, momento(8), momento(10))
    assert respuesta.status_code == 201
    assert respuesta.json()["estado"] == "pendiente"


def test_intervalos_contiguos(cliente):
    admin = administrador(cliente)
    sala = espacio(cliente, admin)
    ana, _ = solicitante(cliente)
    assert pedir(cliente, ana, sala, momento(8), momento(10)).status_code == 201
    sembrar(cliente, "Luis", "luis@uninpahu.edu.co", "clave-luis", "solicitante")
    luis = token_de(cliente, "luis@uninpahu.edu.co", "clave-luis")
    respuesta = pedir(cliente, luis, sala, momento(10), momento(11))
    assert respuesta.status_code == 201
    assert respuesta.json()["estado"] == "pendiente"


def test_solape_de_un_segundo(cliente):
    admin = administrador(cliente)
    sala = espacio(cliente, admin)
    ana, _ = solicitante(cliente)
    assert pedir(cliente, ana, sala, momento(9, 30, 1), momento(10, 0, 1)).status_code == 201
    sembrar(cliente, "Luis", "luis@uninpahu.edu.co", "clave-luis", "solicitante")
    luis = token_de(cliente, "luis@uninpahu.edu.co", "clave-luis")
    respuesta = pedir(cliente, luis, sala, momento(10, 0, 0), momento(10, 30, 0))
    assert respuesta.status_code == 409
    assert respuesta.json()["codigo"] == "espacio_no_disponible"


def test_disponibilidad_incluye_pendiente_y_aprobada(cliente):
    admin = administrador(cliente)
    sala = espacio(cliente, admin)
    otro = espacio(cliente, admin, "LAB-02")
    ana, ana_id = solicitante(cliente)
    assert pedir(cliente, ana, sala, momento(8), momento(9)).status_code == 201
    insertar(cliente, sala, ana_id, momento(9), momento(10), "aprobada")
    insertar(cliente, otro, ana_id, momento(8), momento(9), "pendiente")
    respuesta = cliente.get(
        f"/api/espacios/{sala}/disponibilidad",
        headers=auth(ana),
        params={"desde": momento(7), "hasta": momento(12)},
    )
    assert respuesta.status_code == 200
    ocupados = respuesta.json()["ocupados"]
    assert len(ocupados) == 2
    assert {item["estado"] for item in ocupados} == {"pendiente", "aprobada"}


def test_disponibilidad_omite_rechazada(cliente):
    admin = administrador(cliente)
    sala = espacio(cliente, admin)
    _, ana_id = solicitante(cliente)
    token = token_de(cliente, "ana@uninpahu.edu.co", "clave-ana")
    insertar(cliente, sala, ana_id, momento(8), momento(10), "rechazada")
    respuesta = cliente.get(
        f"/api/espacios/{sala}/disponibilidad",
        headers=auth(token),
        params={"desde": momento(7), "hasta": momento(12)},
    )
    assert respuesta.status_code == 200
    assert respuesta.json()["ocupados"] == []
