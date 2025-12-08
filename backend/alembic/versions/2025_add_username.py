"""add username to users

Revision ID: 2025_add_username
Revises: 175109880801
Create Date: 2025-12-05 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '2025_add_username'
down_revision: Union[str, None] = '175109880801'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('usuarios', sa.Column('username', sa.String(length=50), nullable=True))
    
    # Populate existing records
    op.execute("UPDATE usuarios SET username = split_part(email, '@', 1) WHERE username IS NULL")
    
    op.create_index(op.f('ix_usuarios_username'), 'usuarios', ['username'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_usuarios_username'), table_name='usuarios')
    op.drop_column('usuarios', 'username')