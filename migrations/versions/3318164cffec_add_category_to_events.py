"""add category to events

Revision ID: 3318164cffec
Revises: db151969f892
Create Date: 2026-04-14 18:51:40.475864

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3318164cffec'
down_revision: Union[str, Sequence[str], None] = 'db151969f892'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column('events', sa.Column('category', sa.String(length=100), nullable=True))

def downgrade():
    op.drop_column('events', 'category')
