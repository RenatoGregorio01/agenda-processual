from datetime import date, timedelta
from uuid import uuid4

from app.core.config import Settings
from app.models.prazo import Prazo, StatusPrazo
from app.models.user import Role, User
from app.services.alertas import _montar_corpo, selecionar_candidatos


def _prazo(**kwargs) -> Prazo:
    today = date.today()
    base = {
        "id": uuid4(),
        "escritorio_id": uuid4(),
        "numero_processo": "0001",
        "cliente": "Cliente",
        "acao": "Ação",
        "data_vencimento": today + timedelta(days=3),
        "responsavel": "Verônica",
        "responsavel_id": uuid4(),
        "status": StatusPrazo.pendente,
    }
    base.update(kwargs)
    return Prazo(**base)


def test_seleciona_alerta_3_dias() -> None:
    hoje = date(2026, 8, 9)
    prazo = _prazo(data_vencimento=hoje + timedelta(days=3))
    candidatos = selecionar_candidatos([(prazo, [3, 1])], hoje=hoje)
    assert len(candidatos) == 1
    assert candidatos[0].dias == 3


def test_seleciona_alertas_personalizados() -> None:
    hoje = date(2026, 8, 9)
    p7 = _prazo(data_vencimento=hoje + timedelta(days=7))
    p1 = _prazo(data_vencimento=hoje + timedelta(days=1))
    assert selecionar_candidatos([(p7, [7, 3, 1])], hoje=hoje)[0].dias == 7
    assert selecionar_candidatos([(p1, [7, 3, 1])], hoje=hoje)[0].dias == 1


def test_respeita_alerta_nao_configurado() -> None:
    hoje = date(2026, 8, 9)
    prazo = _prazo(data_vencimento=hoje + timedelta(days=2))
    assert selecionar_candidatos([(prazo, [3, 1])], hoje=hoje) == []


def test_ignora_cumprido_e_sem_responsavel() -> None:
    hoje = date(2026, 8, 9)
    cumprido = _prazo(
        data_vencimento=hoje + timedelta(days=1),
        status=StatusPrazo.cumprido,
    )
    sem_resp = _prazo(
        data_vencimento=hoje + timedelta(days=1),
        responsavel_id=None,
    )
    assert selecionar_candidatos([(cumprido, [1]), (sem_resp, [1])], hoje=hoje) == []


def test_user_receber_alertas_default() -> None:
    user = User(
        escritorio_id=uuid4(),
        email="a@b.com",
        nome="A",
        hashed_password="x",
        role=Role.editor,
    )
    assert user.receber_alertas is False


def test_email_corpo_nao_inclui_dados_do_cliente() -> None:
    prazo = _prazo(
        id=uuid4(),
        numero_processo="0001234-56.2024.4.01.0000",
        cliente="Maria Souza",
        acao="Protocolar contestação",
        data_vencimento=date(2026, 8, 12),
        responsavel="Verônica",
    )
    settings = Settings(app_public_url="http://localhost:3000")
    subject, text_body, html_body = _montar_corpo(prazo, 3, settings)
    assert "3 dias" in subject
    assert "Protocolar contestação" not in subject
    assert "0001234-56.2024.4.01.0000" not in text_body
    assert "Maria Souza" not in text_body
    assert "Maria Souza" not in html_body
    assert f"http://localhost:3000/prazos/{prazo.id}" in text_body
    assert f"http://localhost:3000/prazos/{prazo.id}" in html_body
    assert "Verônica" not in html_body
    assert "Abrir prazo no sistema" in html_body
    assert "não inclui dados" in html_body


def test_email_alerta_um_dia_usa_urgencia() -> None:
    prazo = _prazo(id=uuid4(), data_vencimento=date(2026, 8, 10))
    settings = Settings(app_public_url="http://localhost:3000")
    subject, _, html_body = _montar_corpo(prazo, 1, settings)
    assert "1 dia" in subject
    assert "Prazo amanhã" in html_body
    assert "#b54708" in html_body
