from datetime import datetime, timedelta, timezone

import pytest

from sigrea.dominio.errores import ErrorNegocio
from sigrea.dominio.tiempo import bloque_supera_cuatro_horas, exigir_intervalo, se_cruzan

UTC = timezone.utc


def t(hora, minuto=0, segundo=0):
    return datetime(2026, 10, 26, hora, minuto, segundo, tzinfo=UTC)


def test_solape_parcial():
    assert se_cruzan(t(8), t(10), t(9), t(11))


def test_contiguos_no_se_cruzan():
    assert not se_cruzan(t(8), t(10), t(10), t(11))


def test_un_segundo_se_cruza():
    assert se_cruzan(t(9, 30, 1), t(10, 0, 1), t(10, 0, 0), t(10, 30, 0))


def test_otro_intervalo_distinto_no_se_cruza():
    assert not se_cruzan(t(8), t(9), t(11), t(12))


def test_treinta_minutos_exactos_se_aceptan():
    inicio, fin = exigir_intervalo(t(8), t(8, 30))
    assert fin - inicio == timedelta(minutes=30)


def test_cuatro_horas_exactas_no_superan_el_bloque():
    assert not bloque_supera_cuatro_horas(t(8), t(12), [])


def test_un_minuto_sobre_cuatro_horas_supera_el_bloque():
    assert bloque_supera_cuatro_horas(t(8), t(12, 1), [])


def test_encadenar_hasta_cuatro_horas_no_supera():
    assert not bloque_supera_cuatro_horas(t(10), t(12), [(t(8), t(10))])


def test_encadenar_un_minuto_de_mas_supera():
    assert bloque_supera_cuatro_horas(t(10), t(12, 1), [(t(8), t(10))])


def test_un_hueco_no_une_el_bloque():
    assert not bloque_supera_cuatro_horas(t(10, 1), t(14), [(t(8), t(10))])


def test_veintinueve_minutos_se_rechazan():
    with pytest.raises(ErrorNegocio) as error:
        exigir_intervalo(t(8), t(8, 29))
    assert error.value.codigo == "datos_invalidos"


def test_instante_sin_zona_se_rechaza():
    with pytest.raises(ErrorNegocio) as error:
        exigir_intervalo(datetime(2026, 10, 26, 8, 0), t(10))
    assert error.value.codigo == "datos_invalidos"
