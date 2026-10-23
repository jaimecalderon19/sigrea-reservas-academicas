from sigrea.infraestructura.modelos import Espacio, Reserva, Usuario


def usuario(item: Usuario) -> dict:
    return {
        "id": item.id,
        "nombre": item.nombre,
        "correo": item.correo,
        "rol": item.rol,
        "activo": item.activo,
    }


def instante(valor) -> str | None:
    if valor is None:
        return None
    return valor.isoformat()


def espacio(item: Espacio) -> dict:
    return {
        "id": item.id,
        "codigo": item.codigo,
        "nombre": item.nombre,
        "tipo": item.tipo,
        "capacidad": item.capacidad,
        "ubicacion": item.ubicacion,
        "activo": item.activo,
    }


def reserva(item: Reserva) -> dict:
    return {
        "id": item.id,
        "espacio_id": item.espacio_id,
        "solicitante_id": item.solicitante_id,
        "inicio": instante(item.inicio),
        "fin": instante(item.fin),
        "proposito": item.proposito,
        "estado": item.estado,
        "nota_revision": item.nota_revision,
        "revisor_id": item.revisor_id,
        "revisado_en": instante(item.revisado_en),
        "nota_cancelacion": item.nota_cancelacion,
        "cancelado_por_id": item.cancelado_por_id,
        "cancelado_en": instante(item.cancelado_en),
        "creado_en": instante(item.creado_en),
    }
