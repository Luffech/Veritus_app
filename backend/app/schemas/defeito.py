from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from app.models.testing import StatusDefeitoEnum, SeveridadeDefeitoEnum
from .execucao_teste import ExecucaoTesteResponse

class DefeitoBase(BaseModel):
    titulo: str
    descricao: str
    evidencias: Optional[str] = None # 
    severidade: SeveridadeDefeitoEnum = SeveridadeDefeitoEnum.medio
    status: StatusDefeitoEnum = StatusDefeitoEnum.aberto
    execucao_teste_id: int 

class DefeitoCreate(DefeitoBase):
    pass

class DefeitoUpdate(BaseModel):
    titulo: Optional[str] = None
    descricao: Optional[str] = None
    evidencias: Optional[str] = None
    severidade: Optional[SeveridadeDefeitoEnum] = None
    status: Optional[StatusDefeitoEnum] = None

class DefeitoResponse(DefeitoBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    execucao: Optional[ExecucaoTesteResponse] = None    
    caso_teste_nome: Optional[str] = None
    projeto_nome: Optional[str] = None
    responsavel_teste_nome: Optional[str] = None
    responsavel_projeto_nome: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)