from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

# --- AUXILIARES ---

# Schema enxuto pra retornar dados de usuário dentro de outras listas (evita loop infinito e dados sensíveis).
class UsuarioSimple(BaseModel):
    id: int
    nome: str
    username: str
    model_config = ConfigDict(from_attributes=True)

# --- PASSOS (STEPS) ---

class PassoCasoTesteBase(BaseModel):
    ordem: int
    acao: str
    resultado_esperado: str

class PassoCasoTesteCreate(PassoCasoTesteBase):
    pass

# Retorna o passo com IDs e datas. Importante pra edição e exibição.
class PassoCasoTesteResponse(PassoCasoTesteBase):
    id: int
    caso_teste_id: int
    
    # Opcional pra não quebrar se o banco retornar nulo em legados.
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

# --- CASO DE TESTE (HEADER) ---

class CasoTesteBase(BaseModel):
    nome: str
    descricao: Optional[str] = None
    pre_condicoes: Optional[str] = None
    criterios_aceitacao: Optional[str] = None
    prioridade: str = "media"

# Payload de criação: recebe o cabeçalho + a lista de passos e já permite alocar (ciclo/responsável).
class CasoTesteCreate(CasoTesteBase):
    responsavel_id: Optional[int] = None
    ciclo_id: Optional[int] = None
    passos: List[PassoCasoTesteCreate] = []

# Payload de atualização: tudo opcional. A lista de passos aqui substitui ou atualiza a existente.
class CasoTesteUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    pre_condicoes: Optional[str] = None
    criterios_aceitacao: Optional[str] = None
    prioridade: Optional[str] = None
    responsavel_id: Optional[int] = None
    passos: Optional[List[dict]] = None 

# Objeto completo devolvido pra tela, com os passos aninhados e o objeto do responsável.
class CasoTesteResponse(CasoTesteBase):
    id: int
    projeto_id: int
    responsavel_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Nesting dos relacionamentos
    responsavel: Optional[UsuarioSimple] = None
    passos: List[PassoCasoTesteResponse] = [] 

    model_config = ConfigDict(from_attributes=True)