import asyncio
from database import async_session_maker
from models import User, Attraction
from security import get_password_hash
from sqlalchemy import select

async def seed_db():
    async with async_session_maker() as session:
        result = await session.execute(select(User).where(User.username == "admin"))
        admin = result.scalar_one_or_none()
        
        if not admin:
            admin = User(
                username="admin",
                email="admin@achinsk-tourism.ru",
                hashed_password=get_password_hash("admin123"),
                is_active=True
            )
            session.add(admin)
            await session.commit()
            await session.refresh(admin)
            print(f"Создан администратор: {admin.username} (id={admin.id})")
        else:
            print(f"Администратор {admin.username} уже существует (id={admin.id})")
        
        result = await session.execute(select(Attraction).where(Attraction.name == "Ачинский краеведческий музей"))
        if not result.scalar_one_or_none():
            museum = Attraction(
                name="Ачинский краеведческий музей",
                description="Главный музей города, хранящий богатую историю края.",
                address="г. Ачинск, пр. Ленина, 1",
                latitude=56.2692,
                longitude=90.4995,
                photo_url="/static/images/museum.jpg",
                created_by=admin.id
            )
            session.add(museum)
            await session.commit()
            await session.refresh(museum)
            print(f"Создана достопримечательность: {museum.name} (id={museum.id})")
        else:
            print("Достопримечательность 'Ачинский краеведческий музей' уже существует")

if __name__ == "__main__":
    asyncio.run(seed_db())