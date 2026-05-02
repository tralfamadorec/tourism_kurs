import asyncio
import sys
sys.path.insert(0, '.')

from database import engine
from models import Base, Food  # Убедитесь, что в models.py есть class Food(Base)

async def init_db():
    async with engine.begin() as conn:
        # Создаст все таблицы, описанные в models.py (включая foods)
        await conn.run_sync(Base.metadata.create_all)
        print("✅ Таблица 'foods' успешно создана!")

if __name__ == "__main__":
    asyncio.run(init_db())