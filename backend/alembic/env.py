# em backend/alembic/env.py
import asyncio
from logging.config import fileConfig
from pathlib import Path
import sys

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import pool

from alembic import context

# Adiciona o diretório raiz do projeto ao path do Python
# para que o Alembic possa encontrar os seus módulos (app.core, app.models)
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.config import settings
from app.core.database import Base
from app.models import * # Importa todos os seus modelos para que o Alembic os "veja"

# Esta é a configuração do Alembic, que lê o ficheiro .ini
config = context.config

# Interpreta o ficheiro de configuração para o logging do Python.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Define os metadados para a operação de 'autogenerate'
# O Alembic compara estes metadados com o estado da base de dados
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Executa migrações no modo 'offline'.
    Não vamos usar isto, mas está aqui por completude.
    """
    url = settings.ASYNC_DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online() -> None:
    """Executa migrações no modo 'online' (conectado à base de dados).
    Este é o modo que vamos usar.
    """
    connectable = create_async_engine(
        settings.ASYNC_DATABASE_URL,
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())