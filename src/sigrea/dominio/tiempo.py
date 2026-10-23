from datetime import datetime, timedelta, timezone

from sigrea.dominio.errores import ErrorNegocio

MINIMO = timedelta(minutes=30)


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


def se_cruzan(
    inicio: datetime, fin: datetime, otro_inicio: datetime, otro_fin: datetime
) -> bool:
    return inicio < otro_fin and fin > otro_inicio
