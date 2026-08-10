from fastapi import APIRouter

from app.api.v1.endpoints import (
    alertas,
    auditoria,
    auth,
    calendario,
    convites,
    feriados,
    health,
    prazos,
    processos,
    roles,
    usuarios,
)

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(prazos.router, prefix="/prazos", tags=["prazos"])
api_router.include_router(processos.router, prefix="/processos", tags=["processos"])
api_router.include_router(auditoria.router, prefix="/auditoria", tags=["auditoria"])
api_router.include_router(usuarios.router, prefix="/usuarios", tags=["usuarios"])
api_router.include_router(roles.router, prefix="/roles", tags=["roles"])
api_router.include_router(alertas.router, prefix="/alertas", tags=["alertas"])
api_router.include_router(feriados.router, prefix="/feriados", tags=["feriados"])
api_router.include_router(calendario.router, prefix="/calendario", tags=["calendario"])
api_router.include_router(convites.router, prefix="/convites", tags=["convites"])
