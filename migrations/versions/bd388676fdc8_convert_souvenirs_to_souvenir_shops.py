"""convert souvenirs to souvenir shops

Revision ID: bd388676fdc8
Revises: 3c5107b923a4
Create Date: 2026-04-17 16:29:03.663634

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bd388676fdc8'
down_revision: Union[str, Sequence[str], None] = '3c5107b923a4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Добавляем новые поля для магазинов
    op.add_column('souvenirs', sa.Column('working_hours', sa.String(length=100), nullable=True))
    # Если поле category уже есть — пропускаем, если нет — раскомментируйте:
    # op.add_column('souvenirs', sa.Column('category', sa.String(length=100), nullable=True))
    
    # Удаляем поля товара (если они есть)
    op.drop_column('souvenirs', 'producer')
    op.drop_column('souvenirs', 'price')

def downgrade() -> None:
    # Откат: возвращаем старые поля
    op.add_column('souvenirs', sa.Column('price', sa.Integer(), nullable=True))
    op.add_column('souvenirs', sa.Column('producer', sa.String(length=255), nullable=True))
    
    op.drop_column('souvenirs', 'working_hours')
    # op.drop_column('souvenirs', 'category')  # если добавляли
