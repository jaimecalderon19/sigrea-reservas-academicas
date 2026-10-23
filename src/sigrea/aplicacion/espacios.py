from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from sigrea.dominio.errores import ErrorNegocio
from sigrea.infraestructura.modelos import Espacio, Usuario

TIPOS = {"laboratorio", "auditorio", "sala_computo"}


def crear_espacio(
    db: Session,
    actor: Usuario,
    codigo: str,
    nombre: str,
    tipo: str,
    capacidad: int,
    ubicacion: str,
) -> Espacio:
    if actor.rol != "administrador":
        raise ErrorNegocio("prohibido", "Solo el administrador crea espacios")
    if tipo not in TIPOS:
        raise ErrorNegocio("datos_invalidos", "Tipo de espacio no admitido")
    if capacidad < 1:
        raise ErrorNegocio("datos_invalidos", "La capacidad debe ser positiva")
    if not codigo.strip() or not nombre.strip() or not ubicacion.strip():
        raise ErrorNegocio("datos_invalidos", "Codigo, nombre y ubicacion son obligatorios")
    espacio = Espacio(
        codigo=codigo.strip(),
        nombre=nombre.strip(),
        tipo=tipo,
        capacidad=capacidad,
        ubicacion=ubicacion.strip(),
        activo=True,
    )
    db.add(espacio)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ErrorNegocio("codigo_duplicado", "El codigo ya existe") from None
    db.refresh(espacio)
    return espacio


def listar_espacios(db: Session) -> list[Espacio]:
    return db.query(Espacio).order_by(Espacio.id).all()


def obtener_espacio(db: Session, espacio_id: int) -> Espacio:
    espacio = db.get(Espacio, espacio_id)
    if espacio is None:
        raise ErrorNegocio("no_encontrado", "El espacio no existe")
    return espacio


def actualizar_espacio(
    db: Session,
    actor: Usuario,
    espacio_id: int,
    datos: dict,
) -> Espacio:
    if actor.rol != "administrador":
        raise ErrorNegocio("prohibido", "Solo el administrador modifica espacios")
    espacio = obtener_espacio(db, espacio_id)
    if "tipo" in datos and datos["tipo"] is not None:
        if datos["tipo"] not in TIPOS:
            raise ErrorNegocio("datos_invalidos", "Tipo de espacio no admitido")
        espacio.tipo = datos["tipo"]
    if "capacidad" in datos and datos["capacidad"] is not None:
        if datos["capacidad"] < 1:
            raise ErrorNegocio("datos_invalidos", "La capacidad debe ser positiva")
        espacio.capacidad = datos["capacidad"]
    if "codigo" in datos and datos["codigo"] is not None:
        espacio.codigo = datos["codigo"].strip()
    if "nombre" in datos and datos["nombre"] is not None:
        if not datos["nombre"].strip():
            raise ErrorNegocio("datos_invalidos", "El nombre es obligatorio")
        espacio.nombre = datos["nombre"].strip()
    if "ubicacion" in datos and datos["ubicacion"] is not None:
        if not datos["ubicacion"].strip():
            raise ErrorNegocio("datos_invalidos", "La ubicacion es obligatoria")
        espacio.ubicacion = datos["ubicacion"].strip()
    if "activo" in datos and datos["activo"] is not None:
        espacio.activo = datos["activo"]
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ErrorNegocio("codigo_duplicado", "El codigo ya existe") from None
    db.refresh(espacio)
    return espacio
