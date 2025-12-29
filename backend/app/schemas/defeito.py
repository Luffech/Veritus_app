from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from app.models.testing import StatusDefeitoEnum, SeveridadeDefeitoEnum
from .execucao_teste import ExecucaoTesteResponse

# Campos padrão do Bug Report.
class DefeitoBase(BaseModel):
    titulo: str
    descricao: str
    evidencias: Optional[str] = None # Link ou base64
    severidade: SeveridadeDefeitoEnum = SeveridadeDefeitoEnum.medio
    status: StatusDefeitoEnum = StatusDefeitoEnum.aberto
    execucao_teste_id: int # Link obrigatório com a execução onde falhou

class DefeitoCreate(DefeitoBase):
    pass

class DefeitoUpdate(BaseModel):
    titulo: Optional[str] = None
    descricao: Optional[str] = None
    evidencias: Optional[str] = None
    severidade: Optional[SeveridadeDefeitoEnum] = None
    status: Optional[StatusDefeitoEnum] = None

# Retorna o defeito com os dados da execução atrelada pra contexto.
class DefeitoResponse(DefeitoBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    execucao: Optional[ExecucaoTesteResponse] = None
    
    model_config = ConfigDict(from_attributes=True)