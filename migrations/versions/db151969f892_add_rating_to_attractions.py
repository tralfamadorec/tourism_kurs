"""add rating to attractions

Revision ID: db151969f892
Revises: cacc962c5a42
Create Date: 2026-04-14 18:30:47.469306

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'db151969f892'
down_revision: Union[str, Sequence[str], None] = 'cacc962c5a42'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column('attractions', sa.Column('rating', sa.Float(), nullable=True))

def downgrade():
    op.drop_column('attractions', 'rating')
    