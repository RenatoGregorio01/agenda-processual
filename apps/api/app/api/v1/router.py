from fastapi import APIRouter

from app.api.v1.endpoints import auditoria, auth, health, prazos

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(prazos.router, prefix="/prazos", tags=["prazos"])
api_router.include_router(auditoria.router, prefix="/auditoria", tags=["auditoria"])
