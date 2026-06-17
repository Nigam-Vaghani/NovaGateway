"""Add request_logs table

Revision ID: 3a47e3e894df
Revises: 
Create Date: 2026-06-17 17:09:08.489788

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3a47e3e894df'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'request_logs',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=True),
        sa.Column('client_ip', sa.String(), nullable=True),
        sa.Column('method', sa.String(), nullable=True),
        sa.Column('path', sa.String(), nullable=True),
        sa.Column('target_backend', sa.String(), nullable=True),
        sa.Column('status_code', sa.Integer(), nullable=True),
        sa.Column('latency_ms', sa.Float(), nullable=True),
        sa.Column('response_size', sa.Integer(), nullable=True),
        sa.Column('error', sa.String(), nullable=True),
        sa.Column('cache_hit', sa.Boolean(), default=False, nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('request_logs')
