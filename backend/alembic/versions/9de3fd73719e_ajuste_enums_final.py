"""ajuste_enums_final

Revision ID: 9de3fd73719e
Revises: a647078590ee
Create Date: 2026-01-20 18:08:27.372684

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '9de3fd73719e'
down_revision: Union[str, None] = 'a647078590ee'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE status_execucao_enum RENAME TO status_execucao_enum_old")

    op.execute("CREATE TYPE status_execucao_enum AS ENUM('pendente', 'em_progresso', 'reteste', 'fechado')")

    op.execute("""
        ALTER TABLE execucoes_teste 
        ALTER COLUMN status_geral TYPE status_execucao_enum 
        USING (
            CASE status_geral::text
                WHEN 'passou' THEN 'fechado'::status_execucao_enum
                WHEN 'falhou' THEN 'fechado'::status_execucao_enum
                WHEN 'bloqueado' THEN 'fechado'::status_execucao_enum
                WHEN 'fechado' THEN 'fechado'::status_execucao_enum
                WHEN 'reteste' THEN 'reteste'::status_execucao_enum
                WHEN 'pendente' THEN 'pendente'::status_execucao_enum
                WHEN 'em_progresso' THEN 'em_progresso'::status_execucao_enum
                ELSE 'pendente'::status_execucao_enum
            END
        )
    """)

    op.execute("DROP TYPE status_execucao_enum_old")


def downgrade() -> None:
    op.execute("ALTER TYPE status_execucao_enum RENAME TO status_execucao_enum_new")
    op.execute("CREATE TYPE status_execucao_enum AS ENUM('pendente', 'em_progresso', 'passou', 'falhou', 'bloqueado', 'fechado', 'reteste')")
    
    op.execute("""
        ALTER TABLE execucoes_teste 
        ALTER COLUMN status_geral TYPE status_execucao_enum 
        USING status_geral::text::status_execucao_enum
    """)
    op.execute("DROP TYPE status_execucao_enum_new")