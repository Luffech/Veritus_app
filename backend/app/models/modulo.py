from sqlalchemy import Column, Integer, String, Boolean, Text, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Modulo(Base):
    __tablename__ = "modulos"

    id = Column(Integer, primary_key=True, index=True)
    sistema_id = Column(Integer, ForeignKey("sistemas.id"), nullable=False)
    nome = Column(String(255), nullable=False)
    descricao = Column(Text)
    ordem = Column(Integer)
    ativo = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relacionamento
    sistema = relationship("Sistema", back_populates="modulos", foreign_keys=[sistema_id])
    projetos = relationship("Projeto", back_populates="modulo", foreign_keys="[Projeto.modulo_id]")