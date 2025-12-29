import enum
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum
from sqlalchemy.dialects.postgresql import JSONB 
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

# Define os papéis fixos do sistema pra evitar strings soltas ("magic strings") no código.
class NivelAcessoEnum(str, enum.Enum):
    admin = "admin"
    user = "user"

# Tabela que gerencia os perfis de acesso e as permissões detalhadas de cada um.
class NivelAcesso(Base):
    __tablename__ = "niveis_acesso"

    id = Column(Integer, primary_key=True, index=True)
    
    # Usa o Enum pra garantir que o banco só aceite valores válidos (admin/user).
    nome = Column(Enum(NivelAcessoEnum, name='nivel_acesso_enum', create_type=False), nullable=False)    
    
    descricao = Column(Text)
    
    # Guarda um JSON flexível com as regras específicas (ex: {'can_delete': false}).
    permissoes = Column(JSONB)    
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Link reverso para listar todos os usuários que possuem este perfil.
    usuarios = relationship("Usuario", back_populates="nivel_acesso")