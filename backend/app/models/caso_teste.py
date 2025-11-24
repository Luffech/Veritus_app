from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

# Define o ENUM 'prioridade_caso_teste_enum' sem tentar recriá-lo
prioridade_enum = ENUM('alta', 'media', 'baixa', name='prioridade_caso_teste_enum', create_type=False)

class CasoTeste(Base):
    __tablename__ = "casos_teste"

    id = Column(Integer, primary_key=True, index=True)
    ciclo_teste_id = Column(Integer, ForeignKey("ciclos_teste.id"), nullable=False)
    projeto_id = Column(Integer, ForeignKey("projetos.id"), nullable=False)
    nome = Column(String(255), nullable=False)
    descricao = Column(Text)
    passos = Column(Text)
    criterios_aceitacao = Column(Text)
    prioridade = Column(prioridade_enum, default='media')
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relacionamento
    projeto = relationship("Projeto", back_populates="casos_teste", foreign_keys=[projeto_id])
    ciclos_teste = relationship("CicloTeste", back_populates="caso_teste", foreign_keys="[CicloTeste.casos_teste_id]")
    tentativas = relationship("RegistroTentativaTeste", back_populates="caso_teste", foreign_keys="[RegistroTentativaTeste.caso_teste_id]")