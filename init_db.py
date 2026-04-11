import asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker
from database import engine, Base, async_session_maker
from models import Attraction, User

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all, checkfirst=True)
    print("Таблицы успешно созданы в базе данных!")

if __name__ == "__main__":
    asyncio.run(init_db())