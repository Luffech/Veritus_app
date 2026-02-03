from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class LogSistema(Base):
    __tablename__ = "logs_sistema"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    sistema_id = Column(Integer, ForeignKey("sistemas.id"), nullable=True)
    entidade_nome = Column(String, nullable=True)
    acao = Column(String)
    entidade = Column(String)
    entidade_id = Column(Integer) 
    detalhes = Column(String)
    created_at = Column(DateTime(timezone=False), server_default=func.now())

    usuario = relationship("Usuario", back_populates="logs")
    sistema = relationship("Sistema", back_populates="logs")