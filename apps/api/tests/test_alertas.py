from datetime import date, timedelta
from uuid import uuid4

from app.models.prazo import Prazo, StatusPrazo
from app.models.user import Role, User
from app.services.alertas import selecionar_candidatos


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
