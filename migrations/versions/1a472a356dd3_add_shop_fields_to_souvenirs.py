"""add shop fields to souvenirs

Revision ID: 1a472a356dd3
Revises: bd388676fdc8
Create Date: 2026-04-17 16:42:12.776874

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1a472a356dd3'
down_revision: Union[str, Sequence[str], None] = 'bd388676fdc8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Добавляем поля для сувенирных магазинов
    op.add_column('souvenirs', sa.Column('address', sa.String(length=255), nullable=True))
    op.add_column('souvenirs', sa.Column('phone', sa.String(length=20), nullable=True))
    op.add_column('souvenirs', sa.Column('website', sa.String(length=255), nullable=True))
    op.add_column('souvenirs', sa.Column('working_hours', sa.String(length=100), nullable=True))
    op.add_column('souvenirs', sa.Column('latitude', sa.Float(), nullable=True))
    op.add_column('souvenirs', sa.Column('longitude', sa.Float(), nullable=True))
    # Поле category уже должно быть, если нет — раскомментируйте:
    # op.add_column('souvenirs', sa.Column('category', sa.String(length=100), nullable=True))
    op.add_column('souvenirs', sa.Column('is_accessible', sa.Boolean(), nullable=True))
    
    # Удаляем старые поля товара (если они ещё есть)
    # op.drop_column('souvenirs', 'producer')  # если было
    # op.drop_column('souvenirs', 'price')     # если было

def downgrade() -> None:
    """Downgrade schema."""
    # Откат: удаляем новые поля
    op.drop_column('souvenirs', 'is_accessible')
    op.drop_column('souvenirs', 'longitude')
    op.drop_column('souvenirs', 'latitude')
    op.drop_column('souvenirs', 'working_hours')
    op.drop_column('souvenirs', 'website')
    op.drop_column('souvenirs', 'phone')
    op.drop_column('souvenirs', 'address')
    # op.drop_column('souvenirs', 'category')
    
    # Возвращаем старые поля (если нужно)
    # op.add_column('souvenirs', sa.Column('price', sa.Integer(), nullable=True))
    # op.add_column('souvenirs', sa.Column('producer', sa.String(length=255), nullable=True))
