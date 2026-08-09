from pydantic import BaseModel


class ProcessarAlertasResponse(BaseModel):
    candidatos: int
    enviados: int
    ignorados: int
    erros: int
