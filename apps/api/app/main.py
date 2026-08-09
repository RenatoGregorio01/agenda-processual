from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.database import AsyncSessionLocal, init_db
from app.core.scheduler import start_scheduler, stop_scheduler
from app.core.seed import seed_admin_user, seed_example_prazos


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings = get_settings()
    await init_db()
    async with AsyncSessionLocal() as session:
        await seed_admin_user(session, settings)
        await seed_example_prazos(session)
    start_scheduler()
    yield
    stop_scheduler()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix=settings.api_v1_prefix)
    return app


app = create_app()
