from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from enum import Enum

# Enum simples pra controlar o ciclo de vida do projeto.
class StatusProjeto(str, Enum):
    ativo = "ativo"
    pausado = "pausado"
    finalizado = "finalizado"

class ProjetoBase(BaseModel):
    nome: str
    descricao: Optional[str] = None
    status: Optional[StatusProjeto] = StatusProjeto.ativo
    sistema_id: int
    modulo_id: int
    responsavel_id: Optional[int] = None    

class ProjetoCreate(ProjetoBase):
    pass

# Payload de edição. Atenção ao trocar sistema_id/modulo_id pra não deixar órfão.
class ProjetoUpdate(BaseModel):
    nome: str
    descricao: Optional[str] = None
    status: Optional[StatusProjeto] = None
    sistema_id: int
    modulo_id: int
    responsavel_id: Optional[int] = None   

class ProjetoResponse(ProjetoBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)