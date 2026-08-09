from datetime import date, timedelta
from uuid import uuid4

from app.core.config import Settings
from app.models.alerta_envio import TipoAlerta
from app.models.prazo import Prazo, StatusPrazo
from app.models.user import Role, User
from app.services.alertas import _montar_corpo, selecionar_candidatos


def _prazo(**kwargs) -> Prazo:
    today = date.today()
    base = {
        "id": uuid4(),
        "numero_processo": "0001",
        "cliente": "Cliente",
        "acao": "Ação",
        "data_vencimento": today + timedelta(days=3),
        "responsavel": "Verônica",
        "responsavel_id": uuid4(),
        "status": StatusPrazo.pendente,
        "alerta_3_dias": True,
        "alerta_2_dias": True,
        "alerta_1_dia": True,
    }
    base.update(kwargs)
    return Prazo(**base)


def test_seleciona_alerta_3_dias() -> None:
    hoje = date(2026, 8, 9)
    prazo = _prazo(data_vencimento=hoje + timedelta(days=3))
    candidatos = selecionar_candidatos([prazo], hoje=hoje)
    assert len(candidatos) == 1
    assert candidatos[0].dias == 3
    assert candidatos[0].tipo == TipoAlerta.dias_3


def test_seleciona_alertas_2_e_1_dia() -> None:
    hoje = date(2026, 8, 9)
    p2 = _prazo(data_vencimento=hoje + timedelta(days=2))
    p1 = _prazo(data_vencimento=hoje + timedelta(days=1))
    assert selecionar_candidatos([p2], hoje=hoje)[0].tipo == TipoAlerta.dias_2
    assert selecionar_candidatos([p1], hoje=hoje)[0].tipo == TipoAlerta.dias_1


def test_respeita_flag_desligado() -> None:
    hoje = date(2026, 8, 9)
    prazo = _prazo(data_vencimento=hoje + timedelta(days=2), alerta_2_dias=False)
    assert selecionar_candidatos([prazo], hoje=hoje) == []


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
    assert selecionar_candidatos([cumprido, sem_resp], hoje=hoje) == []


def test_user_receber_alertas_default() -> None:
    user = User(
        email="a@b.com",
        nome="A",
        hashed_password="x",
        role=Role.editor,
    )
    assert user.receber_alertas is True


def test_email_corpo_inclui_dados_do_prazo() -> None:
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
    assert "Protocolar contestação" in subject
    assert "0001234-56.2024.4.01.0000" in text_body
    assert "Maria Souza" in text_body
    assert f"http://localhost:3000/prazos/{prazo.id}" in text_body
    assert "Verônica" in html_body
