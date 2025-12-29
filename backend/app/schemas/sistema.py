from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

# Base com campos comuns. O Sistema é a raiz da árvore (Sistema -> Módulo -> Projeto).
class SistemaBase(BaseModel):
    nome: str
    descricao: str | None = None

# Payload de entrada (POST).
class SistemaCreate(SistemaBase):
    pass 

# Payload de atualização (PUT/PATCH)
class SistemaUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    ativo: Optional[bool] = None

# O que o front recebe. Vem com timestamps pra auditoria.
class SistemaResponse(SistemaBase):
    id: int
    nome: str
    ativo: bool
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)