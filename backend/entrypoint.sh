#!/bin/sh
set -e
set -x

echo "Iniciando processo de migração..."

# 1. Aplica migrações existentes primeiro
echo "Aplicando migrações existentes..."
alembic upgrade head

# 2. Verifica se PRECISA gerar nova migração
echo "Verificando se modelos foram atualizados..."
if alembic check; then
    echo "Nenhuma mudança detectada nos modelos."
else
    echo "Mudanças detectadas! Gerando nova migração..."
    alembic revision --autogenerate -m "Auto: $(date '+%Y-%m-%d %H:%M')"
    
    echo "Aplicando nova migração..."
    alembic upgrade head
    echo "Migração automática concluída!"
fi

echo "Verificando/Inserindo dados iniciais..."
python -m app.initial_data

echo "Iniciando aplicação..."
exec "$@"