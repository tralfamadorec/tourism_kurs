"""add is_accessible to all venues

Revision ID: 3c5107b923a4
Revises: 76b0f4577ecb
Create Date: 2026-04-16 22:36:50.061940

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3c5107b923a4'
down_revision: Union[str, Sequence[str], None] = '76b0f4577ecb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('accommodations', sa.Column('is_accessible', sa.Boolean(), nullable=True))
    op.add_column('events', sa.Column('is_accessible', sa.Boolean(), nullable=True))
    op.add_column('foods', sa.Column('is_accessible', sa.Boolean(), nullable=True))
    op.add_column('routes', sa.Column('is_accessible', sa.Boolean(), nullable=True))

def downgrade() -> None:
    op.drop_column('routes', 'is_accessible')
    op.drop_column('foods', 'is_accessible')
    op.drop_column('events', 'is_accessible')
    op.drop_column('accommodations', 'is_accessible')
