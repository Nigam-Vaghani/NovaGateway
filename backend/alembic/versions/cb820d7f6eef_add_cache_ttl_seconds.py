"""add_cache_ttl_seconds

Revision ID: cb820d7f6eef
Revises: 085aef49af1a
Create Date: 2026-06-18 15:41:42.404885

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cb820d7f6eef'
down_revision: Union[str, Sequence[str], None] = '085aef49af1a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('routes', sa.Column('cache_ttl_seconds', sa.Integer(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('routes', 'cache_ttl_seconds')
