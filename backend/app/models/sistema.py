from sqlalchemy import Column, Integer, String, Boolean, Text, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Sistema(Base):
    __tablename__ = "sistemas"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    descricao = Column(Text)
    ativo = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relacionamento
    modulos = relationship("Modulo", back_populates="sistema", foreign_keys="[Modulo.sistema_id]")
    projetos = relationship("Projeto", back_populates="sistema", foreign_keys="[Projeto.sistema_id]")