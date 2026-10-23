from fastapi import Depends, FastAPI, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from sigrea.aplicacion.espacios import (
    actualizar_espacio,
    crear_espacio,
    listar_espacios,
    obtener_espacio,
)
from sigrea.aplicacion.identidad import (
    actualizar_cuenta,
    ingresar,
    listar_usuarios,
    registrar,
    salir,
    usuario_de_token,
)
from sigrea.dominio.errores import ErrorNegocio
from sigrea.infraestructura.db import preparar
from sigrea.infraestructura.modelos import Usuario
from sigrea.api.serial import espacio as serializar_espacio
from sigrea.api.serial import usuario as serializar_usuario

ESTADOS = {
    "correo_duplicado": 409,
    "codigo_duplicado": 409,
    "espacio_no_disponible": 409,
    "espacio_inactivo": 409,
    "estado_invalido": 409,
    "credenciales_invalidas": 401,
    "no_autenticado": 401,
    "cuenta_inactiva": 403,
    "prohibido": 403,
    "no_encontrado": 404,
    "datos_invalidos": 400,
}


class RegistroEntrada(BaseModel):
    nombre: str
    correo: str
    clave: str
    rol: str | None = None


class IngresoEntrada(BaseModel):
    correo: str
    clave: str


class CuentaEntrada(BaseModel):
    rol: str | None = None
    activo: bool | None = None


class EspacioEntrada(BaseModel):
    codigo: str
    nombre: str
    tipo: str
    capacidad: int
    ubicacion: str


class EspacioCambio(BaseModel):
    codigo: str | None = None
    nombre: str | None = None
    tipo: str | None = None
    capacidad: int | None = None
    ubicacion: str | None = None
    activo: bool | None = None


def create_app(database_url: str = "sqlite:///./sigrea.db") -> FastAPI:
    fabrica = preparar(database_url)
    app = FastAPI(title="SIGREA")
    app.state.fabrica = fabrica

    def get_db():
        db = fabrica()
        try:
            yield db
        finally:
            db.close()

    def actor(
        db: Session = Depends(get_db),
        authorization: str | None = Header(default=None),
    ) -> Usuario:
        if not authorization or not authorization.startswith("Bearer "):
            raise ErrorNegocio("no_autenticado", "Se requiere una sesion valida")
        token = authorization.removeprefix("Bearer ").strip()
        if not token:
            raise ErrorNegocio("no_autenticado", "Se requiere una sesion valida")
        return usuario_de_token(db, token)

    @app.exception_handler(ErrorNegocio)
    def manejar_error(_request, exc: ErrorNegocio):
        return JSONResponse(
            status_code=ESTADOS.get(exc.codigo, 400),
            content={"codigo": exc.codigo, "mensaje": exc.mensaje},
        )

    @app.get("/api/salud")
    def salud():
        return {"estado": "ok"}

    @app.post("/api/auth/registro", status_code=201)
    def registro(cuerpo: RegistroEntrada, db: Session = Depends(get_db)):
        creado = registrar(db, cuerpo.nombre, cuerpo.correo, cuerpo.clave, cuerpo.rol)
        return serializar_usuario(creado)

    @app.post("/api/auth/ingreso")
    def ingreso(cuerpo: IngresoEntrada, db: Session = Depends(get_db)):
        token, cuenta = ingresar(db, cuerpo.correo, cuerpo.clave)
        return {"token": token, "usuario": serializar_usuario(cuenta)}

    @app.post("/api/auth/salida", status_code=204)
    def salida(
        db: Session = Depends(get_db),
        authorization: str | None = Header(default=None),
    ):
        if authorization and authorization.startswith("Bearer "):
            salir(db, authorization.removeprefix("Bearer ").strip())
        return None

    @app.get("/api/usuarios")
    def usuarios(db: Session = Depends(get_db), actual: Usuario = Depends(actor)):
        return [serializar_usuario(item) for item in listar_usuarios(db, actual)]

    @app.get("/api/usuarios/yo")
    def yo(actual: Usuario = Depends(actor)):
        return serializar_usuario(actual)

    @app.patch("/api/usuarios/{usuario_id}")
    def actualizar(
        usuario_id: int,
        cuerpo: CuentaEntrada,
        db: Session = Depends(get_db),
        actual: Usuario = Depends(actor),
    ):
        cuenta = actualizar_cuenta(db, actual, usuario_id, cuerpo.rol, cuerpo.activo)
        return serializar_usuario(cuenta)

    @app.post("/api/espacios", status_code=201)
    def alta_espacio(
        cuerpo: EspacioEntrada,
        db: Session = Depends(get_db),
        actual: Usuario = Depends(actor),
    ):
        creado = crear_espacio(
            db,
            actual,
            cuerpo.codigo,
            cuerpo.nombre,
            cuerpo.tipo,
            cuerpo.capacidad,
            cuerpo.ubicacion,
        )
        return serializar_espacio(creado)

    @app.get("/api/espacios")
    def espacios(db: Session = Depends(get_db), actual: Usuario = Depends(actor)):
        del actual
        return [serializar_espacio(item) for item in listar_espacios(db)]

    @app.get("/api/espacios/{espacio_id}")
    def espacio_uno(
        espacio_id: int,
        db: Session = Depends(get_db),
        actual: Usuario = Depends(actor),
    ):
        del actual
        return serializar_espacio(obtener_espacio(db, espacio_id))

    @app.patch("/api/espacios/{espacio_id}")
    def cambiar_espacio(
        espacio_id: int,
        cuerpo: EspacioCambio,
        db: Session = Depends(get_db),
        actual: Usuario = Depends(actor),
    ):
        actualizado = actualizar_espacio(
            db, actual, espacio_id, cuerpo.model_dump(exclude_unset=True)
        )
        return serializar_espacio(actualizado)

    return app
