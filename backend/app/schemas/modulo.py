from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

# Base compartilhada. Módulos organizam os projetos dentro de um sistema maior.
class ModuloBase(BaseModel):
    nome: str
    descricao: Optional[str] = None
    ordem: Optional[int] = None # Pra ordenar a exibição no menu lateral
    ativo: bool = True
    sistema_id: int

class ModuloCreate(ModuloBase):
    pass

class ModuloUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    ordem: Optional[int] = None
    ativo: Optional[bool] = None
    sistema_id: Optional[int] = None # Permite mover de sistema se precisar

class ModuloResponse(ModuloBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)