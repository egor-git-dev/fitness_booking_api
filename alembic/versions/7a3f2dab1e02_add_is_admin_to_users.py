"""add is_admin to users

Revision ID: 7a3f2dab1e02
Revises: 8ba6d744875f
Create Date: 2026-03-16 11:27:58.959086

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7a3f2dab1e02'
down_revision: Union[str, Sequence[str], None] = '8ba6d744875f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column(
        'users',
        sa.Column('is_admin', sa.Boolean(), nullable=False, server_default=sa.false())
    )
    # Убираем default после применения, если нужно
    op.alter_column('users', 'is_admin', server_default=None)

def downgrade():
    op.drop_column('users', 'is_admin')
