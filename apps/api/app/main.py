from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.database import AsyncSessionLocal, init_db, run_processo_backfill
from app.core.redis import close_redis, get_redis
from app.core.scheduler import start_scheduler, stop_scheduler
from app.core.seed import corrigir_cnj_exemplos, seed_admin_user, seed_example_prazos


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings = get_settings()
    await init_db()
    await run_processo_backfill()
    async with AsyncSessionLocal() as session:
        await seed_admin_user(session, settings)
        if settings.seed_example_data and settings.app_env != "production":
            await seed_example_prazos(session)
        await corrigir_cnj_exemplos(session)
    await run_processo_backfill()
    await get_redis()
    start_scheduler()
    yield
    stop_scheduler()
    await close_redis()


def _cors_origins(settings) -> list[str]:
    origins = [item.strip() for item in settings.cors_origins.split(",") if item.strip()]
    public = settings.app_public_url.rstrip("/")
    if public and public not in origins:
        origins.append(public)
    return origins


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=_cors_origins(settings),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix=settings.api_v1_prefix)

    if settings.metrics_enabled:
        try:
            from prometheus_fastapi_instrumentator import Instrumentator

            Instrumentator(
                should_group_status_codes=True,
                excluded_handlers=["/metrics", "/api/v1/health"],
            ).instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)
        except ImportError:
            # Imagem antiga sem o pacote: API sobe sem /metrics até rebuild.
            pass

    return app


app = create_app()

