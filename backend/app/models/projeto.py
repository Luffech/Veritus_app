# em app/models/projeto.py
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB, ENUM
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

# Define o ENUM sem tentar criá-lo de novo na base de dados
status_projeto_enum = ENUM('ativo', 'pausado', 'finalizado', name='status_projeto_enum', create_type=False)

class Projeto(Base):
    __tablename__ = "projetos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    modulo_id = Column(Integer, ForeignKey("modulos.id"), nullable=False)
    sistema_id = Column(Integer, ForeignKey("sistemas.id"), nullable=False)
    responsavel_id = Column(Integer, ForeignKey("usuarios.id"))
    descricao = Column(Text)
    status = Column(status_projeto_enum, default='ativo')
    metricas = Column(JSONB)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relacionamentos
    modulo = relationship("Modulo", back_populates="projetos", foreign_keys=[modulo_id])
    sistema = relationship("Sistema", back_populates="projetos", foreign_keys=[sistema_id])
    responsavel = relationship("Usuario", back_populates="projetos_responsavel", foreign_keys=[responsavel_id])
    casos_teste = relationship("CasoTeste", back_populates="projeto", foreign_keys="[CasoTeste.projeto_id]")
    metricas_rel = relationship("Metrica", back_populates="projeto", foreign_keys="[Metrica.projeto_id]")