import threading
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from sigrea.dominio.errores import ErrorNegocio
from sigrea.dominio.tiempo import exigir_intervalo, exigir_rango, se_cruzan
from sigrea.infraestructura.modelos import Espacio, Reserva, Usuario

ESTADOS_OCUPAN = ("pendiente", "aprobada")
_cerrojo = threading.Lock()


def _leer_utc(valor: datetime) -> datetime:
    if valor.tzinfo is None:
        return valor.replace(tzinfo=timezone.utc)
    return valor.astimezone(timezone.utc)


def hay_cruce(
    db: Session,
    espacio_id: int,
    inicio: datetime,
    fin: datetime,
    excluir_id: int | None = None,
) -> bool:
    filas = (
        db.query(Reserva)
        .filter(
            Reserva.espacio_id == espacio_id,
            Reserva.estado.in_(ESTADOS_OCUPAN),
        )
        .all()
    )
    for fila in filas:
        if excluir_id is not None and fila.id == excluir_id:
            continue
        if se_cruzan(inicio, fin, _leer_utc(fila.inicio), _leer_utc(fila.fin)):
            return True
    return False


def crear_solicitud(
    db: Session,
    actor: Usuario,
    espacio_id: int,
    inicio: datetime,
    fin: datetime,
    proposito: str,
) -> Reserva:
    if actor.rol != "solicitante":
        raise ErrorNegocio("prohibido", "Solo un solicitante crea solicitudes")
    texto = proposito.strip()
    if not texto:
        raise ErrorNegocio("datos_invalidos", "El proposito es obligatorio")
    if len(texto) > 500:
        raise ErrorNegocio("datos_invalidos", "El proposito admite hasta 500 caracteres")
    inicio_utc, fin_utc = exigir_intervalo(inicio, fin)
    with _cerrojo:
        espacio = db.get(Espacio, espacio_id)
        if espacio is None:
            raise ErrorNegocio("no_encontrado", "El espacio no existe")
        if not espacio.activo:
            raise ErrorNegocio("espacio_inactivo", "El espacio no admite reservas")
        if hay_cruce(db, espacio_id, inicio_utc, fin_utc):
            raise ErrorNegocio("espacio_no_disponible", "El espacio no esta disponible")
        reserva = Reserva(
            espacio_id=espacio.id,
            solicitante_id=actor.id,
            inicio=inicio_utc,
            fin=fin_utc,
            proposito=texto,
            estado="pendiente",
            creado_en=datetime.now(timezone.utc),
        )
        db.add(reserva)
        db.commit()
        db.refresh(reserva)
        return reserva


def _visible(actor: Usuario, reserva: Reserva) -> Reserva:
    if actor.rol == "solicitante" and reserva.solicitante_id != actor.id:
        raise ErrorNegocio("prohibido", "No puede operar esa reserva")
    return reserva


def obtener_reserva(db: Session, actor: Usuario, reserva_id: int) -> Reserva:
    reserva = db.get(Reserva, reserva_id)
    if reserva is None:
        if actor.rol == "solicitante":
            raise ErrorNegocio("prohibido", "No puede operar esa reserva")
        raise ErrorNegocio("no_encontrado", "La reserva no existe")
    return _visible(actor, reserva)


def listar_reservas(
    db: Session, actor: Usuario, estado: str | None = None
) -> list[Reserva]:
    if estado is not None and estado not in (
        "pendiente",
        "aprobada",
        "rechazada",
        "cancelada",
    ):
        raise ErrorNegocio("datos_invalidos", "Estado no admitido")
    consulta = db.query(Reserva)
    if actor.rol == "solicitante":
        consulta = consulta.filter(Reserva.solicitante_id == actor.id)
    if estado is not None:
        consulta = consulta.filter(Reserva.estado == estado)
    return consulta.order_by(Reserva.id).all()


def _decidir(
    db: Session, actor: Usuario, reserva_id: int, nota: str, estado: str
) -> Reserva:
    if actor.rol not in ("coordinador", "administrador"):
        raise ErrorNegocio("prohibido", "Solo coordinador o administrador deciden")
    texto = nota.strip()
    if not texto:
        raise ErrorNegocio("datos_invalidos", "La nota de revision es obligatoria")
    with _cerrojo:
        reserva = db.get(Reserva, reserva_id)
        if reserva is None:
            raise ErrorNegocio("no_encontrado", "La reserva no existe")
        if reserva.estado != "pendiente":
            raise ErrorNegocio(
                "estado_invalido", "Solo se decide una solicitud pendiente"
            )
        if estado == "aprobada" and hay_cruce(
            db, reserva.espacio_id, _leer_utc(reserva.inicio), _leer_utc(reserva.fin), reserva.id
        ):
            raise ErrorNegocio("espacio_no_disponible", "El espacio no esta disponible")
        reserva.estado = estado
        reserva.nota_revision = texto
        reserva.revisor_id = actor.id
        reserva.revisado_en = datetime.now(timezone.utc)
        db.commit()
        db.refresh(reserva)
        return reserva


def aprobar(db: Session, actor: Usuario, reserva_id: int, nota: str) -> Reserva:
    return _decidir(db, actor, reserva_id, nota, "aprobada")


def rechazar(db: Session, actor: Usuario, reserva_id: int, nota: str) -> Reserva:
    return _decidir(db, actor, reserva_id, nota, "rechazada")


def cancelar(
    db: Session, actor: Usuario, reserva_id: int, nota: str | None
) -> Reserva:
    with _cerrojo:
        reserva = db.get(Reserva, reserva_id)
        if reserva is None:
            if actor.rol == "solicitante":
                raise ErrorNegocio("prohibido", "No puede operar esa reserva")
            raise ErrorNegocio("no_encontrado", "La reserva no existe")
        if reserva.estado not in ESTADOS_OCUPAN:
            raise ErrorNegocio(
                "estado_invalido", "Solo se cancela una reserva pendiente o aprobada"
            )
        if actor.rol == "solicitante" and reserva.solicitante_id != actor.id:
            raise ErrorNegocio("prohibido", "No puede cancelar la reserva de otro")
        if actor.rol not in ("solicitante", "coordinador", "administrador"):
            raise ErrorNegocio("prohibido", "No puede cancelar esa reserva")
        reserva.estado = "cancelada"
        reserva.nota_cancelacion = (nota or "").strip() or None
        reserva.cancelado_por_id = actor.id
        reserva.cancelado_en = datetime.now(timezone.utc)
        db.commit()
        db.refresh(reserva)
        return reserva


def disponibilidad(
    db: Session, espacio_id: int, desde: datetime, hasta: datetime
) -> list[Reserva]:
    if db.get(Espacio, espacio_id) is None:
        raise ErrorNegocio("no_encontrado", "El espacio no existe")
    desde_utc, hasta_utc = exigir_rango(desde, hasta)
    filas = (
        db.query(Reserva)
        .filter(
            Reserva.espacio_id == espacio_id,
            Reserva.estado.in_(ESTADOS_OCUPAN),
        )
        .order_by(Reserva.inicio)
        .all()
    )
    return [
        fila
        for fila in filas
        if se_cruzan(desde_utc, hasta_utc, _leer_utc(fila.inicio), _leer_utc(fila.fin))
    ]
