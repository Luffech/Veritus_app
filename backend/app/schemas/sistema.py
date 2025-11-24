from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# Schema base com os campos comuns
class SistemaBase(BaseModel):
    nome: str
    descricao: str | None = None

# Schema para a criação de um novo Sistema (o que a API recebe)
class SistemaCreate(SistemaBase):
    pass # Não há campos extras para a criação, herda tudo de SistemaBase

class SistemaUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    ativo: Optional[bool] = None

# Schema para a resposta da API (o que a API devolve)
class SistemaResponse(SistemaBase):
    id: int
    nome: str
    ativo: bool
    created_at: datetime
    updated_at: datetime

    # Configuração para que o Pydantic consiga ler os dados
    # a partir de um objeto SQLAlchemy (o nosso modelo Sistema)
class Config:
    from_attributes = True