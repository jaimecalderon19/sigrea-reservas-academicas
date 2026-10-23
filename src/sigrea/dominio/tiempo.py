from datetime import datetime, timedelta, timezone

from sigrea.dominio.errores import ErrorNegocio

MINIMO = timedelta(minutes=30)
MAXIMO = timedelta(hours=4)


def como_utc(valor: datetime) -> datetime:
    if valor.tzinfo is None:
        raise ErrorNegocio("datos_invalidos", "El instante debe incluir zona horaria")
    return valor.astimezone(timezone.utc)


def exigir_rango(inicio: datetime, fin: datetime) -> tuple[datetime, datetime]:
    if inicio.tzinfo is None or fin.tzinfo is None:
        raise ErrorNegocio("datos_invalidos", "El instante debe incluir zona horaria")
    inicio_utc = inicio.astimezone(timezone.utc)
    fin_utc = fin.astimezone(timezone.utc)
    if fin_utc <= inicio_utc:
        raise ErrorNegocio("datos_invalidos", "El fin debe ser posterior al inicio")
    return inicio_utc, fin_utc


def exigir_intervalo(inicio: datetime, fin: datetime) -> tuple[datetime, datetime]:
    inicio_utc, fin_utc = exigir_rango(inicio, fin)
    if fin_utc - inicio_utc < MINIMO:
        raise ErrorNegocio("datos_invalidos", "La duracion minima es de 30 minutos")
    return inicio_utc, fin_utc


def bloque_supera_cuatro_horas(
    inicio: datetime,
    fin: datetime,
    vecinas: list[tuple[datetime, datetime]],
) -> bool:
    bloque_inicio, bloque_fin = inicio, fin
    pendientes = list(vecinas)
    cambio = True
    while cambio:
        cambio = False
        restantes = []
        for otro_inicio, otro_fin in pendientes:
            if otro_fin < bloque_inicio or otro_inicio > bloque_fin:
                restantes.append((otro_inicio, otro_fin))
                continue
            bloque_inicio = min(bloque_inicio, otro_inicio)
            bloque_fin = max(bloque_fin, otro_fin)
            cambio = True
        pendientes = restantes
    return bloque_fin - bloque_inicio > MAXIMO


def se_cruzan(
    inicio: datetime, fin: datetime, otro_inicio: datetime, otro_fin: datetime
) -> bool:
    return inicio < otro_fin and fin > otro_inicio
