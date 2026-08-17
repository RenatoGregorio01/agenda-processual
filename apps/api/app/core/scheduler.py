import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.config import get_settings
from app.core.database import AsyncSessionLocal
from app.services.alertas import processar_alertas
from app.services.audit import purgar_auditoria

logger = logging.getLogger(__name__)

_scheduler: AsyncIOScheduler | None = None


async def _job_alertas() -> None:
    settings = get_settings()
    if not settings.alertas_enabled:
        logger.info("Job de alertas desabilitado (ALERTAS_ENABLED=false)")
        return

    async with AsyncSessionLocal() as session:
        result = await processar_alertas(session, settings=settings)
        logger.info(
            "Alertas processados: candidatos=%s enviados=%s ignorados=%s erros=%s",
            result.candidatos,
            result.enviados,
            result.ignorados,
            result.erros,
        )


async def _job_purge_auditoria() -> None:
    settings = get_settings()
    if not settings.audit_purge_enabled:
        logger.info("Job de purge de auditoria desabilitado (AUDIT_PURGE_ENABLED=false)")
        return

    async with AsyncSessionLocal() as session:
        apagados = await purgar_auditoria(
            session,
            retention_days=settings.audit_retention_days,
            batch_size=settings.audit_purge_batch_size,
        )
        logger.info(
            "Purge de auditoria: apagados=%s retention_days=%s",
            apagados,
            settings.audit_retention_days,
        )


def start_scheduler() -> None:
    global _scheduler
    settings = get_settings()
    if _scheduler is not None:
        return

    jobs: list[str] = []
    if settings.alertas_enabled:
        jobs.append("alertas")
    if settings.audit_purge_enabled:
        jobs.append("audit_purge")
    if not jobs:
        logger.info("Scheduler não iniciado (alertas e purge desabilitados)")
        return

    scheduler = AsyncIOScheduler(timezone="America/Sao_Paulo")
    if settings.alertas_enabled:
        scheduler.add_job(
            _job_alertas,
            CronTrigger(hour=settings.alertas_cron_hour, minute=0),
            id="processar_alertas",
            replace_existing=True,
        )
    if settings.audit_purge_enabled:
        scheduler.add_job(
            _job_purge_auditoria,
            CronTrigger(hour=settings.audit_purge_cron_hour, minute=0),
            id="purgar_auditoria",
            replace_existing=True,
        )
    scheduler.start()
    _scheduler = scheduler
    logger.info(
        "Scheduler iniciado (%s)",
        ", ".join(jobs),
    )


def stop_scheduler() -> None:
    global _scheduler
    if _scheduler is None:
        return
    _scheduler.shutdown(wait=False)
    _scheduler = None
