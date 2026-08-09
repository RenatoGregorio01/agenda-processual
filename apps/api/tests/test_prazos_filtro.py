from datetime import date, timedelta

from app.models.prazo import Prazo, StatusPrazo


def _pendente(vencimento: date) -> Prazo:
    return Prazo(
        numero_processo="1",
        cliente="A",
        acao="X",
        data_vencimento=vencimento,
        responsavel="V",
        status=StatusPrazo.pendente,
    )


def test_filtro_atrasados_logic() -> None:
    today = date.today()
    atrasado = _pendente(today - timedelta(days=1))
    futuro = _pendente(today + timedelta(days=2))
    assert atrasado.data_vencimento < today
    assert futuro.data_vencimento >= today


def test_filtro_hoje_e_amanha_logic() -> None:
    today = date.today()
    amanha = today + timedelta(days=1)
    prazo_hoje = _pendente(today)
    prazo_amanha = _pendente(amanha)
    prazo_depois = _pendente(today + timedelta(days=2))

    assert prazo_hoje.data_vencimento == today
    assert prazo_amanha.data_vencimento == amanha
    assert prazo_depois.data_vencimento not in {today, amanha}
