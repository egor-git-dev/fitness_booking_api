"""add is_admin column

Revision ID: 41bf9efbd7ca
Revises: 7a3f2dab1e02
Create Date: 2026-03-16 11:45:24.128117

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '41bf9efbd7ca'
down_revision: Union[str, Sequence[str], None] = '7a3f2dab1e02'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
