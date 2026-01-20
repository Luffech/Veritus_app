"""ajuste_final_enums

Revision ID: a647078590ee
Revises: d1ff55dcad97
Create Date: 2026-01-20 17:59:36.136951

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'a647078590ee'
down_revision: Union[str, None] = 'd1ff55dcad97'
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
                WHEN 'em_progresso' THEN 'em_progresso'::status_execucao_enum
                WHEN 'pendente' THEN 'pendente'::status_execucao_enum
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