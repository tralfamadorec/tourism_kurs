"""add coordinates to foods

Revision ID: 76b0f4577ecb
Revises: eb844475b79e
Create Date: 2026-04-14 23:34:05.137986

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '76b0f4577ecb'
down_revision: Union[str, Sequence[str], None] = 'eb844475b79e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Добавляем колонки latitude и longitude в таблицу foods
    op.add_column('foods', sa.Column('latitude', sa.Float(), nullable=True))
    op.add_column('foods', sa.Column('longitude', sa.Float(), nullable=True))

def downgrade():
    # Удаляем колонки при откате
    op.drop_column('foods', 'longitude')
    op.drop_column('foods', 'latitude')
