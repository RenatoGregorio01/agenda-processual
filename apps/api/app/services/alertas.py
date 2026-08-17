import logging
from dataclasses import dataclass
from datetime import date, timedelta
from uuid import UUID

from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import Settings, get_settings
from app.core.metrics import record_alertas_result
from app.models.alerta_envio import AlertaEnvio
from app.models.prazo import Prazo, StatusPrazo
from app.models.prazo_alerta import PrazoAlerta
from app.models.user import User
from app.schemas.prazo import PrazoAlertaRead, PrazoRead
from app.services.email import send_email

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AlertaCandidato:
    prazo: Prazo
    dias: int


@dataclass
class ProcessamentoAlertasResult:
    candidatos: int = 0
    enviados: int = 0
    ignorados: int = 0
    erros: int = 0


async def list_alertas_read(session: AsyncSession, prazo_id: UUID) -> list[PrazoAlertaRead]:
    result = await session.exec(
        select(PrazoAlerta)
        .where(PrazoAlerta.prazo_id == prazo_id)
        .order_by(col(PrazoAlerta.dias_antes).desc())
    )
    enviados_result = await session.exec(
        select(AlertaEnvio.dias_antes).where(AlertaEnvio.prazo_id == prazo_id).distinct()
    )
    enviados = set(enviados_result.all())
    return [
        PrazoAlertaRead(dias_antes=item.dias_antes, enviado=item.dias_antes in enviados)
        for item in result.all()
    ]


async def to_prazo_read(session: AsyncSession, prazo: Prazo) -> PrazoRead:
    return PrazoRead.model_validate(prazo, from_attributes=True).model_copy(
        update={"alertas": await list_alertas_read(session, prazo.id)}
    )


async def to_prazos_read(session: AsyncSession, prazos: list[Prazo]) -> list[PrazoRead]:
    return [await to_prazo_read(session, prazo) for prazo in prazos]


async def replace_alertas(
    session: AsyncSession,
    prazo_id: UUID,
    dias: list[int],
) -> None:
    result = await session.exec(select(PrazoAlerta).where(PrazoAlerta.prazo_id == prazo_id))
    for item in result.all():
        await session.delete(item)
    await session.flush()
    for value in dias:
        session.add(PrazoAlerta(prazo_id=prazo_id, dias_antes=value))


def selecionar_candidatos(
    prazos: list[tuple[Prazo, list[int]]],
    hoje: date | None = None,
) -> list[AlertaCandidato]:
    ref = hoje or date.today()
    candidatos: list[AlertaCandidato] = []
    for prazo, dias_list in prazos:
        if prazo.status != StatusPrazo.pendente or prazo.excluido_em is not None:
            continue
        if prazo.responsavel_id is None:
            continue
        for dias in dias_list:
            if prazo.data_vencimento == ref + timedelta(days=dias):
                candidatos.append(AlertaCandidato(prazo=prazo, dias=dias))
    return candidatos


async def _destinatarios(session: AsyncSession, prazo: Prazo) -> list[str]:
    if prazo.responsavel_id is None:
        return []
    responsavel = await session.get(User, prazo.responsavel_id)
    if (
        responsavel is None
        or not responsavel.ativo
        or not responsavel.receber_alertas
        or responsavel.escritorio_id != prazo.escritorio_id
    ):
        return []
    return [responsavel.email.lower()]


def _montar_corpo(prazo: Prazo, dias: int, settings: Settings) -> tuple[str, str, str]:
    vencimento = prazo.data_vencimento.strftime("%d/%m/%Y")
    label_dias = "1 dia" if dias == 1 else f"{dias} dias"
    subject = f"[Agenda Processual] Prazo em {label_dias}"
    link = f"{settings.app_public_url.rstrip('/')}/prazos/{prazo.id}"

    text_body = (
        f"Olá,\n\n"
        f"Há um prazo vencendo em {label_dias} ({vencimento}).\n\n"
        f"Os detalhes estão no sistema, após o login.\n\n"
        f"Abrir no sistema: {link}\n"
    )
    html_body = (
        f"<p>Olá,</p>"
        f"<p>Há um prazo vencendo em <strong>{label_dias}</strong> ({vencimento}).</p>"
        f"<p>Os detalhes estão no sistema, após o login.</p>"
        f'<p><a href="{link}">Abrir no sistema</a></p>'
    )
    return subject, text_body, html_body


async def _ja_enviado(
    session: AsyncSession,
    prazo_id: UUID,
    dias_antes: int,
    email: str,
) -> bool:
    result = await session.exec(
        select(AlertaEnvio).where(
            AlertaEnvio.prazo_id == prazo_id,
            AlertaEnvio.dias_antes == dias_antes,
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
    prazos = list(prazos_result.all())
    ids = [prazo.id for prazo in prazos]
    alertas_por_prazo: dict[UUID, list[int]] = {prazo.id: [] for prazo in prazos}
    if ids:
        alertas_result = await session.exec(
            select(PrazoAlerta).where(col(PrazoAlerta.prazo_id).in_(ids))
        )
        for item in alertas_result.all():
            alertas_por_prazo.setdefault(item.prazo_id, []).append(item.dias_antes)

    candidatos = selecionar_candidatos(
        [(prazo, alertas_por_prazo.get(prazo.id, [])) for prazo in prazos],
        hoje=ref,
    )
    result.candidatos = len(candidatos)

    for candidato in candidatos:
        destinatarios = await _destinatarios(session, candidato.prazo)
        subject, text_body, html_body = _montar_corpo(candidato.prazo, candidato.dias, cfg)

        for email in destinatarios:
            if await _ja_enviado(session, candidato.prazo.id, candidato.dias, email):
                result.ignorados += 1
                continue
            from_email, from_name = cfg.from_alerta()
            try:
                await send_email(
                    settings=cfg,
                    to_email=email,
                    subject=subject,
                    text_body=text_body,
                    html_body=html_body,
                    from_email=from_email,
                    from_name=from_name,
                )
            except Exception:
                logger.exception(
                    "Falha ao enviar alerta de %s dias do prazo %s",
                    candidato.dias,
                    candidato.prazo.id,
                )
                result.erros += 1
                continue

            session.add(
                AlertaEnvio(
                    escritorio_id=candidato.prazo.escritorio_id,
                    prazo_id=candidato.prazo.id,
                    dias_antes=candidato.dias,
                    destinatario_email=email,
                )
            )
            result.enviados += 1

    await session.commit()
    record_alertas_result(
        candidatos=result.candidatos,
        enviados=result.enviados,
        erros=result.erros,
        ignorados=result.ignorados,
    )
    return result
