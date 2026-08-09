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


def test_filtro_responsavel_logic() -> None:
    from uuid import uuid4

    responsavel_a = uuid4()
    responsavel_b = uuid4()
    prazo_a = _pendente(date.today())
    prazo_a.responsavel_id = responsavel_a
    prazo_b = _pendente(date.today())
    prazo_b.responsavel_id = responsavel_b

    filtrados = [
        prazo
        for prazo in [prazo_a, prazo_b]
        if prazo.responsavel_id == responsavel_a
    ]
    assert filtrados == [prazo_a]


def test_busca_match_logic() -> None:
    prazo = _pendente(date.today())
    prazo.numero_processo = "0001234-56.2024.4.01.0000"
    prazo.cliente = "Maria Souza"
    prazo.acao = "Protocolar contestação"
    prazo.responsavel = "Verônica"

    term = "maria"
    haystack = " ".join(
        [prazo.numero_processo, prazo.cliente, prazo.acao, prazo.responsavel]
    ).lower()
    assert term in haystack
    assert "recurso" not in haystack
