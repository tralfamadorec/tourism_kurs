"""add coordinates to restaurants

Revision ID: eb844475b79e
Revises: 6bde054842b9
Create Date: 2026-04-14 23:25:55.115496

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'eb844475b79e'
down_revision: Union[str, Sequence[str], None] = '6bde054842b9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column('restaurants', sa.Column('latitude', sa.Float(), nullable=True))
    op.add_column('restaurants', sa.Column('longitude', sa.Float(), nullable=True))

def downgrade():
    op.drop_column('restaurants', 'longitude')
    op.drop_column('restaurants', 'latitude')
