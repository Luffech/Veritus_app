from sqlalchemy import Column, Integer, String, Text, DECIMAL, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

# Define o ENUM 'tipo_metrica_enum' sem tentar recriá-lo na base de dados
tipo_metrica_enum = ENUM('cobertura', 'eficiencia', 'defeitos', 'qualidade', 'produtividade', name='tipo_metrica_enum', create_type=False)

class Metrica(Base):
    __tablename__ = "metricas"

    id = Column(Integer, primary_key=True, index=True)
    projeto_id = Column(Integer, ForeignKey("projetos.id"), nullable=False)
    ciclo_teste_id = Column(Integer, ForeignKey("ciclos_teste.id"))
    tipo_metrica = Column(tipo_metrica_enum, nullable=False)
    casos_reprovados = Column(Integer, nullable=False)
    casos_executados = Column(Integer, nullable=False)
    casos_aprovados = Column(Integer, nullable=False)
    tempo_medio_resolucao = Column(Integer)
    data_medicao = Column(TIMESTAMP(timezone=True), server_default=func.now())
    nome_metrica = Column(String(255), nullable=False)
    valor_metrica = Column(DECIMAL(10, 2), nullable=False)
    unidade_medida = Column(String(255))
    descricao = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relacionamentos
    projeto = relationship("Projeto", back_populates="metricas_rel", foreign_keys=[projeto_id])
    ciclo_teste = relationship("CicloTeste", back_populates="metricas", foreign_keys=[ciclo_teste_id])