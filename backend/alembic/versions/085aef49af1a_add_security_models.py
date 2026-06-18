"""Add security models

Revision ID: 085aef49af1a
Revises: a5f8e91c7b8d
Create Date: 2026-06-18 15:11:52.141615

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '085aef49af1a'
down_revision: Union[str, Sequence[str], None] = 'a5f8e91c7b8d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add require_api_key to routes
    op.add_column('routes', sa.Column('require_api_key', sa.Boolean(), server_default='false', nullable=False))
    
    # Create ip_rules table
    op.create_table('ip_rules',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('ip_cidr', sa.String(), nullable=False),
        sa.Column('rule_type', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('ip_cidr')
    )
    
    # Create api_keys table
    op.create_table('api_keys',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('key', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_api_keys_key'), 'api_keys', ['key'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_api_keys_key'), table_name='api_keys')
    op.drop_table('api_keys')
    op.drop_table('ip_rules')
    op.drop_column('routes', 'require_api_key')
