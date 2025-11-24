from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import settings # Importa a nossa instância de configurações

# Cria a engine assíncrona usando a URL que acabámos de montar
engine = create_async_engine(settings.ASYNC_DATABASE_URL, echo=True)

# Cria a fábrica de sessões assíncronas
AsyncSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, autocommit=False, autoflush=False
)

# Base para os nossos modelos ORM
Base = declarative_base()