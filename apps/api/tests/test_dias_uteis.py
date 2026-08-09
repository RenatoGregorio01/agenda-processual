from datetime import date

import pytest

from app.services.dias_uteis import add_business_days, is_business_day


def test_fim_de_semana_nao_e_dia_util() -> None:
    feriados: set[date] = set()
    assert is_business_day(date(2026, 8, 10), feriados)  # segunda
    assert not is_business_day(date(2026, 8, 15), feriados)  # sábado
    assert not is_business_day(date(2026, 8, 16), feriados)  # domingo


def test_feriado_nao_e_dia_util() -> None:
    feriados = {date(2026, 9, 7)}
    assert not is_business_day(date(2026, 9, 7), feriados)


def test_conta_dias_uteis_pulando_fim_de_semana() -> None:
    # sexta 2026-08-07 + 1 dia útil = segunda 2026-08-10
    assert add_business_days(date(2026, 8, 7), 1, set()) == date(2026, 8, 10)


def test_conta_dias_uteis_com_feriado() -> None:
    # segunda 2026-09-07 é feriado; base sexta 04/09 + 1 útil = terça 08/09
    feriados = {date(2026, 9, 7)}
    assert add_business_days(date(2026, 9, 4), 1, feriados) == date(2026, 9, 8)


def test_quinze_dias_uteis() -> None:
    # base 2026-08-10 (seg) + 15 úteis = 2026-08-31
    assert add_business_days(date(2026, 8, 10), 15, set()) == date(2026, 8, 31)


def test_dias_invalidos() -> None:
    with pytest.raises(ValueError):
        add_business_days(date(2026, 8, 10), 0, set())
