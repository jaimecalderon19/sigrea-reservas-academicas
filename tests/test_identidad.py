from tests.conftest import auth, sembrar, token_de


def test_registro_valido_crea_solicitante_activo(cliente):
    respuesta = cliente.post(
        "/api/auth/registro",
        json={"nombre": "Ana Ruiz", "correo": "ana@uninpahu.edu.co", "clave": "clave-ana"},
    )
    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["rol"] == "solicitante"
    assert cuerpo["activo"] is True
    assert cuerpo["correo"] == "ana@uninpahu.edu.co"
    assert "clave" not in cuerpo


def test_registro_como_administrador_no_crea_cuenta(cliente):
    respuesta = cliente.post(
        "/api/auth/registro",
        json={
            "nombre": "Intruso",
            "correo": "intruso@uninpahu.edu.co",
            "clave": "clave-intruso",
            "rol": "administrador",
        },
    )
    assert respuesta.status_code == 400
    assert respuesta.json()["codigo"] == "datos_invalidos"
    ingreso = cliente.post(
        "/api/auth/ingreso",
        json={"correo": "intruso@uninpahu.edu.co", "clave": "clave-intruso"},
    )
    assert ingreso.status_code == 401


def test_correo_duplicado_sin_distinguir_mayusculas(cliente):
    cliente.post(
        "/api/auth/registro",
        json={"nombre": "Ana", "correo": "admin@uninpahu.edu.co", "clave": "clave-ana"},
    )
    respuesta = cliente.post(
        "/api/auth/registro",
        json={"nombre": "Otra", "correo": "Admin@uninpahu.edu.co", "clave": "clave-otra"},
    )
    assert respuesta.status_code == 409
    assert respuesta.json()["codigo"] == "correo_duplicado"


def test_ingreso_con_credenciales_correctas(cliente):
    cliente.post(
        "/api/auth/registro",
        json={"nombre": "Ana", "correo": "ana@uninpahu.edu.co", "clave": "clave-ana"},
    )
    respuesta = cliente.post(
        "/api/auth/ingreso",
        json={"correo": "ana@uninpahu.edu.co", "clave": "clave-ana"},
    )
    assert respuesta.status_code == 200
    assert respuesta.json()["token"]
    assert respuesta.json()["usuario"]["correo"] == "ana@uninpahu.edu.co"


def test_clave_incorrecta_no_entrega_token(cliente):
    cliente.post(
        "/api/auth/registro",
        json={"nombre": "Ana", "correo": "ana@uninpahu.edu.co", "clave": "clave-ana"},
    )
    respuesta = cliente.post(
        "/api/auth/ingreso",
        json={"correo": "ana@uninpahu.edu.co", "clave": "no-es"},
    )
    assert respuesta.status_code == 401
    assert respuesta.json()["codigo"] == "credenciales_invalidas"
    assert "token" not in respuesta.json()


def test_cuenta_inactiva_no_ingresa(cliente):
    sembrar(cliente, "Ana", "ana@uninpahu.edu.co", "clave-ana", "solicitante", activo=False)
    respuesta = cliente.post(
        "/api/auth/ingreso",
        json={"correo": "ana@uninpahu.edu.co", "clave": "clave-ana"},
    )
    assert respuesta.status_code == 403
    assert respuesta.json()["codigo"] == "cuenta_inactiva"
    assert "token" not in respuesta.json()


def test_token_despues_de_salir_es_rechazado(cliente):
    cliente.post(
        "/api/auth/registro",
        json={"nombre": "Ana", "correo": "ana@uninpahu.edu.co", "clave": "clave-ana"},
    )
    token = token_de(cliente, "ana@uninpahu.edu.co", "clave-ana")
    salida = cliente.post("/api/auth/salida", headers=auth(token))
    assert salida.status_code == 204
    respuesta = cliente.get("/api/usuarios/yo", headers=auth(token))
    assert respuesta.status_code == 401
    assert respuesta.json()["codigo"] == "no_autenticado"


def test_administrador_cambia_el_rol(cliente):
    sembrar(cliente, "Ada", "ada@uninpahu.edu.co", "clave-ada", "administrador")
    sembrar(cliente, "Leo", "leo@uninpahu.edu.co", "clave-leo", "solicitante")
    token = token_de(cliente, "ada@uninpahu.edu.co", "clave-ada")
    leo = cliente.get("/api/usuarios", headers=auth(token)).json()
    leo_id = next(item["id"] for item in leo if item["correo"] == "leo@uninpahu.edu.co")
    respuesta = cliente.patch(
        f"/api/usuarios/{leo_id}",
        headers=auth(token),
        json={"rol": "coordinador"},
    )
    assert respuesta.status_code == 200
    assert respuesta.json()["rol"] == "coordinador"


def test_solicitante_no_administra_cuentas(cliente):
    sembrar(cliente, "Ada", "ada@uninpahu.edu.co", "clave-ada", "administrador")
    sembrar(cliente, "Ana", "ana@uninpahu.edu.co", "clave-ana", "solicitante")
    token = token_de(cliente, "ana@uninpahu.edu.co", "clave-ana")
    respuesta = cliente.patch(
        "/api/usuarios/1",
        headers=auth(token),
        json={"rol": "administrador"},
    )
    assert respuesta.status_code == 403
    assert respuesta.json()["codigo"] == "prohibido"


def test_coordinador_no_desactiva_cuentas(cliente):
    sembrar(cliente, "Coo", "coo@uninpahu.edu.co", "clave-coo", "coordinador")
    sembrar(cliente, "Ana", "ana@uninpahu.edu.co", "clave-ana", "solicitante")
    token = token_de(cliente, "coo@uninpahu.edu.co", "clave-coo")
    ana_id = cliente.app.state.fabrica
    db = ana_id()
    try:
        from sigrea.infraestructura.modelos import Usuario

        cuenta = db.query(Usuario).filter_by(correo="ana@uninpahu.edu.co").one()
        identificador = cuenta.id
    finally:
        db.close()
    respuesta = cliente.patch(
        f"/api/usuarios/{identificador}",
        headers=auth(token),
        json={"activo": False},
    )
    assert respuesta.status_code == 403
    assert respuesta.json()["codigo"] == "prohibido"


def test_listado_sin_token_exige_sesion(cliente):
    respuesta = cliente.get("/api/usuarios")
    assert respuesta.status_code == 401
    assert respuesta.json()["codigo"] == "no_autenticado"


def test_unico_administrador_no_se_desactiva(cliente):
    sembrar(cliente, "Ada", "ada@uninpahu.edu.co", "clave-ada", "administrador")
    token = token_de(cliente, "ada@uninpahu.edu.co", "clave-ada")
    yo = cliente.get("/api/usuarios/yo", headers=auth(token)).json()
    respuesta = cliente.patch(
        f"/api/usuarios/{yo['id']}",
        headers=auth(token),
        json={"activo": False},
    )
    assert respuesta.status_code == 400
    assert respuesta.json()["codigo"] == "datos_invalidos"
    sigue = cliente.get("/api/usuarios/yo", headers=auth(token))
    assert sigue.status_code == 200
    assert sigue.json()["activo"] is True
    assert sigue.json()["rol"] == "administrador"


def test_un_administrador_desactiva_a_otro(cliente):
    sembrar(cliente, "Ada", "ada@uninpahu.edu.co", "clave-ada", "administrador")
    sembrar(cliente, "Ben", "ben@uninpahu.edu.co", "clave-ben", "administrador")
    token = token_de(cliente, "ada@uninpahu.edu.co", "clave-ada")
    cuentas = cliente.get("/api/usuarios", headers=auth(token)).json()
    ben_id = next(item["id"] for item in cuentas if item["correo"] == "ben@uninpahu.edu.co")
    respuesta = cliente.patch(
        f"/api/usuarios/{ben_id}",
        headers=auth(token),
        json={"activo": False},
    )
    assert respuesta.status_code == 200
    assert respuesta.json()["activo"] is False
    ada = cliente.get("/api/usuarios/yo", headers=auth(token))
    assert ada.json()["activo"] is True
