import asyncio
from database import async_session_maker
from models import User, Attraction, Accommodation, Event, Restaurant, Route
from security import get_password_hash
from sqlalchemy import select
from datetime import datetime

async def seed_db():
    async with async_session_maker() as session:
        # администратор
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
        
        # достопримечательность
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

        # гостиницы
        accommodations_data = [
            {"name": "Отель Ачинск", "description": "Уютный отель в центре города", "address": "пр. Ленина, 10", "phone": "+71234567890", "rating": 4.5, "price_per_night": 3500},
            {"name": "Мини-гостиница Сибирь", "description": "Экономичный вариант для туристов", "address": "ул. Шоссейная, 5", "phone": "+71234567891", "rating": 3.8, "price_per_night": 1800},
        ]

        for acc_data in accommodations_data:
            result = await session.execute(select(Accommodation).where(Accommodation.name == acc_data["name"]))
            if not result.scalar_one_or_none():
                acc = Accommodation(**acc_data, created_by=admin.id)
                session.add(acc)
                await session.commit()
                await session.refresh(acc)
                print(f"Создана гостиница: {acc.name} (id={acc.id})")
            else:
                print(f"Гостиница '{acc_data['name']}' уже существует")

        # события
        events_data = [
            {"title": "Фестиваль 'Ачинская весна'", "description": "Ежегодный городской праздник", "event_date": datetime(2024, 5, 15, 10, 0), "location": "Центральная площадь"},
            {"title": "Выставка современного искусства", "description": "Работы местных художников", "event_date": datetime(2024, 6, 1, 12, 0), "location": "ДК 'Металлург'"},
        ]

        for ev_data in events_data:
            result = await session.execute(select(Event).where(Event.title == ev_data["title"]))
            if not result.scalar_one_or_none():
                ev = Event(**ev_data, created_by=admin.id)
                session.add(ev)
                await session.commit()
                print(f"Создано событие: {ev.title}")
            else:
                print(f"Событие '{ev_data['title']}' уже существует")

        # рестораны
        restaurants_data = [
            {"name": "Кафе 'Березка'", "description": "Домашняя кухня", "address": "ул. Ленина, 5", "cuisine": "Русская", "avg_price": 800, "rating": 4.5},
            {"name": "Пиццерия 'Италия'", "description": "Лучшая пицца в городе", "address": "пр. Мира, 12", "cuisine": "Итальянская", "avg_price": 1200, "rating": 4.8},
        ]
        
        for r_data in restaurants_data:
            result = await session.execute(select(Restaurant).where(Restaurant.name == r_data["name"]))
            if not result.scalar_one_or_none():
                r = Restaurant(**r_data, created_by=admin.id)
                session.add(r)
                await session.commit()
                print(f"Создан ресторан: {r.name}")
            else:
                print(f"Ресторан '{r_data['name']}' уже существует")

        # маршруты
        routes_data = [
            {"title": "Исторический центр Ачинска", "description": "Пешеходная экскурсия по старинным зданиям", "duration_hours": 2.5, "difficulty": "Лёгкий", "transport_type": "Пешком"},
            {"title": "Музейный квартал", "description": "Посещение краеведческого музея и выставки", "duration_hours": 3.0, "difficulty": "Лёгкий", "transport_type": "Пешком"},
            {"title": "Природный маршрут «Сосновый бор»", "description": "Эко-тропа с смотровыми площадками", "duration_hours": 4.0, "difficulty": "Средний", "transport_type": "Автомобиль"},
            {"title": "Гастрономический тур", "description": "Дегустация местных блюд в кафе города", "duration_hours": 3.5, "difficulty": "Лёгкий", "transport_type": "Пешком"},
            {"title": "Промышленное наследие", "description": "Обзор предприятий и индустриальных объектов", "duration_hours": 5.0, "difficulty": "Средний", "transport_type": "Автобус"},
            {"title": "Семейный маршрут", "description": "Парки, детские площадки и зооуголок", "duration_hours": 2.0, "difficulty": "Лёгкий", "transport_type": "Пешком"},
            {"title": "Вечерний Ачинск", "description": "Освещённые набережные и фонтаны", "duration_hours": 1.5, "difficulty": "Лёгкий", "transport_type": "Пешком"},
        ]

        for r_data in routes_data:
            result = await session.execute(select(Route).where(Route.title == r_data["title"]))
            if not result.scalar_one_or_none():
                r = Route(**r_data, created_by=admin.id)
                session.add(r)
                await session.commit()
                print(f"Создан маршрут: {r.title}")
            else:
                print(f"Маршрут '{r_data['title']}' уже существует")

if __name__ == "__main__":
    asyncio.run(seed_db())