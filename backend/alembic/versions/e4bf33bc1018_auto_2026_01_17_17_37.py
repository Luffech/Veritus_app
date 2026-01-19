"""Auto: 2026-01-17 17:37

Revision ID: e4bf33bc1018
Revises: de4fecd62a71
Create Date: 2026-01-17 17:37:49.402117

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e4bf33bc1018'
down_revision: Union[str, None] = 'de4fecd62a71'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    
    status_enum = sa.Enum('rascunho', 'ativo', 'obsoleto', 'revisao', name='status_caso_teste_enum')
    
    
    status_enum.create(op.get_bind(), checkfirst=True)
    
    
    op.add_column('casos_teste', sa.Column('status', status_enum, server_default='rascunho', nullable=True))


def downgrade():
    
    op.drop_column('casos_teste', 'status')
    
    
    status_enum = sa.Enum('rascunho', 'ativo', 'obsoleto', 'revisao', name='status_caso_teste_enum')
    
    
    status_enum.drop(op.get_bind(), checkfirst=True)
