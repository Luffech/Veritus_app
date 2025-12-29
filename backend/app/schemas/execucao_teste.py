from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional

# Importa schemas pra aninhar na resposta
from app.schemas.caso_teste import CasoTesteResponse, UsuarioSimple, PassoCasoTesteResponse
from app.models.testing import StatusExecucaoEnum

# --- BASES ---

class ExecucaoTesteBase(BaseModel):
    ciclo_teste_id: int
    caso_teste_id: int
    responsavel_id: int
    status_geral: str = "pendente"

class ExecucaoPassoBase(BaseModel):
    status: str 
    resultado_obtido: Optional[str] = None
    evidencias: Optional[str] = None

# --- CREATE ---
# Usado quando alocamos um teste manualmente.
class ExecucaoTesteCreate(ExecucaoTesteBase):
    pass

# --- UPDATE ---
# Usado pelo QA Runner pra marcar passo a passo.
class ExecucaoPassoUpdate(BaseModel):
    status: Optional[str] = None
    resultado_obtido: Optional[str] = None
    evidencias: Optional[str] = None

# --- RESPONSE ---

# Representa uma linha da tabela de execução.
class ExecucaoPassoResponse(ExecucaoPassoBase):
    id: int
    execucao_teste_id: int
    passo_caso_teste_id: int
    
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # Crucial: Traz o texto original pra comparar com o obtido.
    passo_template: Optional[PassoCasoTesteResponse] = None     
    
    model_config = ConfigDict(from_attributes=True)

# Objeto principal do Runner.
class ExecucaoTesteResponse(ExecucaoTesteBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # Traz tudo carregado: o teste original, quem tá fazendo e os passos com status.
    caso_teste: Optional[CasoTesteResponse] = None
    responsavel: Optional[UsuarioSimple] = None
    passos_executados: List[ExecucaoPassoResponse] = []

    model_config = ConfigDict(from_attributes=True)