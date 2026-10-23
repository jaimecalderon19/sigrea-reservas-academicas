import hashlib
import secrets

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from sigrea.dominio.claves import hash_clave, normalizar_correo, verificar_clave
from sigrea.dominio.errores import ErrorNegocio
from sigrea.infraestructura.modelos import Sesion, Usuario

ROLES = {"solicitante", "coordinador", "administrador"}


def crear_cuenta(
    db: Session,
    nombre: str,
    correo: str,
    clave: str,
    rol: str,
    activo: bool = True,
) -> Usuario:
    if not nombre.strip() or not clave:
        raise ErrorNegocio("datos_invalidos", "Nombre y clave son obligatorios")
    if rol not in ROLES:
        raise ErrorNegocio("datos_invalidos", "Rol no admitido")
    try:
        correo_normalizado = normalizar_correo(correo)
    except ValueError:
        raise ErrorNegocio("datos_invalidos", "El correo no es valido") from None
    usuario = Usuario(
        nombre=nombre.strip(),
        correo=correo_normalizado,
        clave_hash=hash_clave(clave),
        rol=rol,
        activo=activo,
    )
    db.add(usuario)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ErrorNegocio("correo_duplicado", "El correo ya existe") from None
    db.refresh(usuario)
    return usuario


def registrar(db: Session, nombre: str, correo: str, clave: str, rol: str | None) -> Usuario:
    pedido = rol or "solicitante"
    if pedido != "solicitante":
        raise ErrorNegocio(
            "datos_invalidos", "El registro publico solo crea solicitantes"
        )
    return crear_cuenta(db, nombre, correo, clave, "solicitante")


def ingresar(db: Session, correo: str, clave: str) -> tuple[str, Usuario]:
    try:
        correo_normalizado = normalizar_correo(correo)
    except ValueError:
        raise ErrorNegocio("credenciales_invalidas", "Credenciales invalidas") from None
    usuario = db.query(Usuario).filter_by(correo=correo_normalizado).first()
    if usuario is None or not verificar_clave(clave, usuario.clave_hash):
        raise ErrorNegocio("credenciales_invalidas", "Credenciales invalidas")
    if not usuario.activo:
        raise ErrorNegocio("cuenta_inactiva", "La cuenta esta inactiva")
    token = secrets.token_urlsafe(32)
    db.add(
        Sesion(
            token_hash=hashlib.sha256(token.encode()).hexdigest(),
            usuario_id=usuario.id,
        )
    )
    db.commit()
    return token, usuario


def salir(db: Session, token: str) -> None:
    digest = hashlib.sha256(token.encode()).hexdigest()
    sesion = db.query(Sesion).filter_by(token_hash=digest).first()
    if sesion is not None:
        db.delete(sesion)
        db.commit()


def usuario_de_token(db: Session, token: str) -> Usuario:
    digest = hashlib.sha256(token.encode()).hexdigest()
    sesion = db.query(Sesion).filter_by(token_hash=digest).first()
    if sesion is None:
        raise ErrorNegocio("no_autenticado", "Se requiere una sesion valida")
    usuario = db.get(Usuario, sesion.usuario_id)
    if usuario is None or not usuario.activo:
        raise ErrorNegocio("no_autenticado", "Se requiere una sesion valida")
    return usuario


def listar_usuarios(db: Session, actor: Usuario) -> list[Usuario]:
    if actor.rol != "administrador":
        raise ErrorNegocio("prohibido", "Solo el administrador lista las cuentas")
    return db.query(Usuario).order_by(Usuario.id).all()


def actualizar_cuenta(
    db: Session,
    actor: Usuario,
    usuario_id: int,
    rol: str | None,
    activo: bool | None,
) -> Usuario:
    if actor.rol != "administrador":
        raise ErrorNegocio("prohibido", "Solo el administrador administra cuentas")
    usuario = db.get(Usuario, usuario_id)
    if usuario is None:
        raise ErrorNegocio("no_encontrado", "La cuenta no existe")
    nuevo_rol = usuario.rol if rol is None else rol
    nuevo_activo = usuario.activo if activo is None else activo
    if nuevo_rol not in ROLES:
        raise ErrorNegocio("datos_invalidos", "Rol no admitido")
    if usuario.rol == "administrador" and usuario.activo:
        pierde_admin = nuevo_rol != "administrador" or not nuevo_activo
        if pierde_admin:
            otros = (
                db.query(Usuario)
                .filter(
                    Usuario.rol == "administrador",
                    Usuario.activo.is_(True),
                    Usuario.id != usuario.id,
                )
                .count()
            )
            if otros == 0:
                raise ErrorNegocio(
                    "datos_invalidos", "Debe quedar un administrador activo"
                )
    usuario.rol = nuevo_rol
    usuario.activo = nuevo_activo
    db.commit()
    db.refresh(usuario)
    return usuario
