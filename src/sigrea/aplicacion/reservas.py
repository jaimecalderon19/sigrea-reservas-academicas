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
