import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.config import get_settings
from app.core.database import AsyncSessionLocal
from app.services.alertas import processar_alertas

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


def start_scheduler() -> None:
    global _scheduler
    settings = get_settings()
    if not settings.alertas_enabled:
        logger.info("Scheduler de alertas não iniciado (ALERTAS_ENABLED=false)")
        return

    if _scheduler is not None:
        return

    scheduler = AsyncIOScheduler(timezone="America/Sao_Paulo")
    scheduler.add_job(
        _job_alertas,
        CronTrigger(hour=settings.alertas_cron_hour, minute=0),
        id="processar_alertas",
        replace_existing=True,
    )
    scheduler.start()
    _scheduler = scheduler
    logger.info(
        "Scheduler de alertas iniciado (cron diário às %02d:00 America/Sao_Paulo)",
        settings.alertas_cron_hour,
    )


def stop_scheduler() -> None:
    global _scheduler
    if _scheduler is None:
        return
    _scheduler.shutdown(wait=False)
    _scheduler = None
