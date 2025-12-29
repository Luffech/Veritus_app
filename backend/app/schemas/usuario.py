from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime
from typing import Optional

# Versão resumida do cargo pra não poluir o JSON de resposta do usuário.
class NivelAcessoSimple(BaseModel):
    id: int
    nome: str
    descricao: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

# Campos comuns que todo usuário tem (login, email, status).
class UsuarioBase(BaseModel):
    nome: str
    username: Optional[str] = None
    email: EmailStr
    nivel_acesso_id: int
    ativo: bool = True

# Payload de cadastro. A senha vem "crua" aqui, mas é hasheada no service antes de salvar.
class UsuarioCreate(UsuarioBase):
    senha: str

# Payload de edição (PATCH). Manda só o que quer alterar; se a senha vier, a gente troca.
class UsuarioUpdate(BaseModel):
    nome: Optional[str] = None
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    senha: Optional[str] = None
    nivel_acesso_id: Optional[int] = None
    ativo: Optional[bool] = None

# O que o frontend vê. Importante: NUNCA retornar o campo 'senha' aqui.
class UsuarioResponse(UsuarioBase):
    id: int
    created_at: datetime
    updated_at: datetime | None = None
    
    # Traz o objeto do cargo aninhado pra facilitar a exibição na grid.
    nivel_acesso: Optional[NivelAcessoSimple] = None
    
    model_config = ConfigDict(from_attributes=True)