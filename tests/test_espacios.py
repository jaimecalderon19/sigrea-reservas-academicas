from tests.conftest import auth, sembrar, token_de


def administrador(cliente) -> str:
    sembrar(cliente, "Ada", "ada@uninpahu.edu.co", "clave-ada", "administrador")
    return token_de(cliente, "ada@uninpahu.edu.co", "clave-ada")


def crear(cliente, token, **extra):
    cuerpo = {
        "codigo": "LAB-01",
        "nombre": "Laboratorio de redes",
        "tipo": "laboratorio",
        "capacidad": 20,
        "ubicacion": "Bloque B",
    }
    cuerpo.update(extra)
    return cliente.post("/api/espacios", headers=auth(token), json=cuerpo)


def test_alta_de_laboratorio(cliente):
    token = administrador(cliente)
    respuesta = crear(cliente, token)
    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["activo"] is True
    assert cuerpo["tipo"] == "laboratorio"
    assert cuerpo["capacidad"] == 20
    assert cuerpo["codigo"] == "LAB-01"
    consulta = cliente.get(f"/api/espacios/{cuerpo['id']}", headers=auth(token))
    assert consulta.status_code == 200
    assert consulta.json()["nombre"] == "Laboratorio de redes"


def test_alta_de_auditorio_y_sala(cliente):
    token = administrador(cliente)
    auditorio = crear(
        cliente,
        token,
        codigo="AUD-01",
        nombre="Auditorio central",
        tipo="auditorio",
        capacidad=120,
    )
    sala = crear(
        cliente,
        token,
        codigo="SAL-01",
        nombre="Sala de computo 1",
        tipo="sala_computo",
        capacidad=30,
    )
    assert auditorio.status_code == 201
    assert sala.status_code == 201
    assert auditorio.json()["tipo"] == "auditorio"
    assert sala.json()["tipo"] == "sala_computo"


def test_capacidad_no_positiva(cliente):
    token = administrador(cliente)
    respuesta = crear(cliente, token, capacidad=0)
    assert respuesta.status_code == 400
    assert respuesta.json()["codigo"] == "datos_invalidos"
    assert cliente.get("/api/espacios", headers=auth(token)).json() == []


def test_tipo_no_admitido(cliente):
    token = administrador(cliente)
    respuesta = crear(cliente, token, tipo="cafeteria")
    assert respuesta.status_code == 400
    assert respuesta.json()["codigo"] == "datos_invalidos"


def test_codigo_duplicado(cliente):
    token = administrador(cliente)
    assert crear(cliente, token).status_code == 201
    respuesta = crear(cliente, token, nombre="Otro")
    assert respuesta.status_code == 409
    assert respuesta.json()["codigo"] == "codigo_duplicado"


def test_coordinador_no_crea_espacios(cliente):
    sembrar(cliente, "Coo", "coo@uninpahu.edu.co", "clave-coo", "coordinador")
    token = token_de(cliente, "coo@uninpahu.edu.co", "clave-coo")
    respuesta = crear(cliente, token)
    assert respuesta.status_code == 403
    assert respuesta.json()["codigo"] == "prohibido"


def test_solicitante_no_crea_espacios(cliente):
    sembrar(cliente, "Ana", "ana@uninpahu.edu.co", "clave-ana", "solicitante")
    token = token_de(cliente, "ana@uninpahu.edu.co", "clave-ana")
    respuesta = crear(cliente, token)
    assert respuesta.status_code == 403
    assert respuesta.json()["codigo"] == "prohibido"


def test_listado_autenticado_incluye_inactivos(cliente):
    token = administrador(cliente)
    creado = crear(cliente, token).json()
    cliente.patch(
        f"/api/espacios/{creado['id']}",
        headers=auth(token),
        json={"activo": False},
    )
    sembrar(cliente, "Ana", "ana@uninpahu.edu.co", "clave-ana", "solicitante")
    ana = token_de(cliente, "ana@uninpahu.edu.co", "clave-ana")
    listado = cliente.get("/api/espacios", headers=auth(ana))
    assert listado.status_code == 200
    assert listado.json()[0]["activo"] is False


def test_identificador_inexistente(cliente):
    token = administrador(cliente)
    respuesta = cliente.get("/api/espacios/999", headers=auth(token))
    assert respuesta.status_code == 404
    assert respuesta.json()["codigo"] == "no_encontrado"


def test_consulta_sin_sesion(cliente):
    respuesta = cliente.get("/api/espacios")
    assert respuesta.status_code == 401
    assert respuesta.json()["codigo"] == "no_autenticado"


def test_desactivar_conserva_el_espacio(cliente):
    token = administrador(cliente)
    creado = crear(cliente, token).json()
    respuesta = cliente.patch(
        f"/api/espacios/{creado['id']}",
        headers=auth(token),
        json={"activo": False},
    )
    assert respuesta.status_code == 200
    assert respuesta.json()["activo"] is False
    sigue = cliente.get(f"/api/espacios/{creado['id']}", headers=auth(token))
    assert sigue.status_code == 200
    assert sigue.json()["codigo"] == "LAB-01"


def test_coordinador_no_desactiva(cliente):
    token = administrador(cliente)
    creado = crear(cliente, token).json()
    sembrar(cliente, "Coo", "coo@uninpahu.edu.co", "clave-coo", "coordinador")
    coo = token_de(cliente, "coo@uninpahu.edu.co", "clave-coo")
    respuesta = cliente.patch(
        f"/api/espacios/{creado['id']}",
        headers=auth(coo),
        json={"activo": False},
    )
    assert respuesta.status_code == 403
    assert respuesta.json()["codigo"] == "prohibido"
