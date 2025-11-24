# em app/models/registro_tentativa_teste.py
from sqlalchemy import Column, Integer, String, Boolean, Text, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class RegistroTentativaTeste(Base):
    __tablename__ = "registro_tentativa_teste" 

    id = Column(Integer, primary_key=True, index=True)
    caso_teste_id = Column(Integer, ForeignKey("casos_teste.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    numero_tentativa = Column(Integer, nullable=False)
    resultado = Column(Boolean, nullable=False)
    evidencias = Column(Text)
    data_execucao = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relacionamentos
    caso_teste = relationship("CasoTeste", back_populates="tentativas", foreign_keys=[caso_teste_id])
    usuario = relationship("Usuario", back_populates="tentativas", foreign_keys=[usuario_id])