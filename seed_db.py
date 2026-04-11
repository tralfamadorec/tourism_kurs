import asyncio
from database import async_session_maker
from models import User, Attraction

async def seed_db():
    async with async_session_maker() as session:
        admin = User(
            username="admin",
            email="admin@achinsk-tourism.ru",
            hashed_password="hashed_secret_123",
            is_active=True
        )
        session.add(admin)

        await session.commit()
        await session.refresh(admin)
        print(f"Создан пользователь: {admin.username} (id={admin.id})")

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

if __name__ == "__main__":
    asyncio.run(seed_db())