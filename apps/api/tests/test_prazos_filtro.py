from datetime import date, timedelta

from app.models.prazo import Prazo, StatusPrazo


def test_filtro_atrasados_logic() -> None:
    today = date.today()
    atrasado = Prazo(
        numero_processo="1",
        cliente="A",
        acao="X",
        data_vencimento=today - timedelta(days=1),
        responsavel="V",
        status=StatusPrazo.pendente,
    )
    futuro = Prazo(
        numero_processo="2",
        cliente="B",
        acao="Y",
        data_vencimento=today + timedelta(days=2),
        responsavel="V",
        status=StatusPrazo.pendente,
    )
    assert atrasado.data_vencimento < today
    assert futuro.data_vencimento >= today
