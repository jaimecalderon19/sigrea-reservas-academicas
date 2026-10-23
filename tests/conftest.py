import pytest
from fastapi.testclient import TestClient

from sigrea.api.app import create_app
from sigrea.aplicacion.identidad import crear_cuenta


@pytest.fixture
def cliente(tmp_path):
    app = create_app(f"sqlite:///{tmp_path / 'sigrea.db'}")
    with TestClient(app) as prueba:
        yield prueba


def sembrar(cliente, nombre, correo, clave, rol, activo=True) -> int:
    db = cliente.app.state.fabrica()
    try:
        cuenta = crear_cuenta(db, nombre, correo, clave, rol, activo)
        return cuenta.id
    finally:
        db.close()


def token_de(cliente, correo, clave) -> str:
    respuesta = cliente.post(
        "/api/auth/ingreso", json={"correo": correo, "clave": clave}
    )
    assert respuesta.status_code == 200, respuesta.text
    return respuesta.json()["token"]


def auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}
