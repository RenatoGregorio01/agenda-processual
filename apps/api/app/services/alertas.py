import logging
from dataclasses import dataclass
from datetime import date, timedelta
from uuid import UUID

from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import Settings, get_settings
from app.models.alerta_envio import AlertaEnvio, TipoAlerta
from app.models.prazo import Prazo, StatusPrazo
from app.models.user import User
from app.services.email import send_email

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AlertaCandidato:
    prazo: Prazo
    tipo: TipoAlerta
    dias: int


@dataclass
class ProcessamentoAlertasResult:
    candidatos: int = 0
    enviados: int = 0
    ignorados: int = 0
    erros: int = 0


def _tipos_alerta() -> list[tuple[TipoAlerta, int, str]]:
    return [
        (TipoAlerta.dias_3, 3, "alerta_3_dias"),
        (TipoAlerta.dias_2, 2, "alerta_2_dias"),
        (TipoAlerta.dias_1, 1, "alerta_1_dia"),
    ]


def selecionar_candidatos(prazos: list[Prazo], hoje: date | None = None) -> list[AlertaCandidato]:
    ref = hoje or date.today()
    candidatos: list[AlertaCandidato] = []
    for prazo in prazos:
        if prazo.status != StatusPrazo.pendente or prazo.excluido_em is not None:
            continue
        if prazo.responsavel_id is None:
            continue
        for tipo, dias, flag in _tipos_alerta():
            if not getattr(prazo, flag):
                continue
            if prazo.data_vencimento == ref + timedelta(days=dias):
                candidatos.append(AlertaCandidato(prazo=prazo, tipo=tipo, dias=dias))
    return candidatos


async def _destinatarios(session: AsyncSession, prazo: Prazo) -> list[str]:
    emails: set[str] = set()

    if prazo.responsavel_id is not None:
        responsavel = await session.get(User, prazo.responsavel_id)
        if responsavel is not None and responsavel.ativo:
            emails.add(responsavel.email.lower())

    result = await session.exec(
        select(User).where(col(User.ativo).is_(True), col(User.receber_alertas).is_(True))
    )
    for user in result.all():
        emails.add(user.email.lower())

    return sorted(emails)


def _montar_corpo(prazo: Prazo, dias: int, settings: Settings) -> tuple[str, str, str]:
    vencimento = prazo.data_vencimento.strftime("%d/%m/%Y")
    label_dias = "1 dia" if dias == 1 else f"{dias} dias"
    subject = f"[Agenda Processual] Prazo em {label_dias}: {prazo.acao}"
    link = f"{settings.app_public_url.rstrip('/')}/prazos/{prazo.id}"

    text_body = (
        f"Olá,\n\n"
        f"Há um prazo vencendo em {label_dias}.\n\n"
        f"Processo: {prazo.numero_processo}\n"
        f"Cliente: {prazo.cliente}\n"
        f"Ação: {prazo.acao}\n"
        f"Vencimento: {vencimento}\n"
        f"Responsável: {prazo.responsavel}\n\n"
        f"Abrir no sistema: {link}\n"
    )
    html_body = (
        f"<p>Olá,</p>"
        f"<p>Há um prazo vencendo em <strong>{label_dias}</strong>.</p>"
        f"<ul>"
        f"<li><strong>Processo:</strong> {prazo.numero_processo}</li>"
        f"<li><strong>Cliente:</strong> {prazo.cliente}</li>"
        f"<li><strong>Ação:</strong> {prazo.acao}</li>"
        f"<li><strong>Vencimento:</strong> {vencimento}</li>"
        f"<li><strong>Responsável:</strong> {prazo.responsavel}</li>"
        f"</ul>"
        f'<p><a href="{link}">Abrir no sistema</a></p>'
    )
    return subject, text_body, html_body


async def _ja_enviado(
    session: AsyncSession,
    prazo_id: UUID,
    tipo: TipoAlerta,
    email: str,
) -> bool:
    result = await session.exec(
        select(AlertaEnvio).where(
            AlertaEnvio.prazo_id == prazo_id,
            AlertaEnvio.tipo == tipo,
            AlertaEnvio.destinatario_email == email,
        )
    )
    return result.first() is not None


async def processar_alertas(
    session: AsyncSession,
    settings: Settings | None = None,
    hoje: date | None = None,
) -> ProcessamentoAlertasResult:
    cfg = settings or get_settings()
    ref = hoje or date.today()
    result = ProcessamentoAlertasResult()

    prazos_result = await session.exec(
        select(Prazo).where(
            Prazo.status == StatusPrazo.pendente,
            col(Prazo.excluido_em).is_(None),
            col(Prazo.responsavel_id).is_not(None),
        )
    )
    candidatos = selecionar_candidatos(list(prazos_result.all()), hoje=ref)
    result.candidatos = len(candidatos)

    for candidato in candidatos:
        destinatarios = await _destinatarios(session, candidato.prazo)
        subject, text_body, html_body = _montar_corpo(candidato.prazo, candidato.dias, cfg)

        for email in destinatarios:
            if await _ja_enviado(session, candidato.prazo.id, candidato.tipo, email):
                result.ignorados += 1
                continue
            try:
                await send_email(
                    settings=cfg,
                    to_email=email,
                    subject=subject,
                    text_body=text_body,
                    html_body=html_body,
                )
            except Exception:
                logger.exception(
                    "Falha ao enviar alerta %s do prazo %s para %s",
                    candidato.tipo,
                    candidato.prazo.id,
                    email,
                )
                result.erros += 1
                continue

            session.add(
                AlertaEnvio(
                    prazo_id=candidato.prazo.id,
                    tipo=candidato.tipo,
                    destinatario_email=email,
                )
            )
            result.enviados += 1

    await session.commit()
    return result
