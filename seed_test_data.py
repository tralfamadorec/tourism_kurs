"""
Скрипт для быстрого наполнения базы тестовыми данными (Ачинск)
Запуск: python seed_test_data.py
"""
import asyncio
import random
from datetime import datetime, timedelta

from database import async_session_maker
from models import (
    Attraction, Accommodation, Food, Event, 
    Souvenir, SafetyObject, Route, PostcardTemplate
)

# Тестовые данные для Ачинска
TEST_DATA = {
    "attractions": [
        {"name": "Краеведческий музей", "address": "г. Ачинск, пр. Мира, 20", "description": "История города с древнейших времён", "latitude": 56.2659, "longitude": 90.4969, "is_accessible": True},
        {"name": "Парк культуры и отдыха", "address": "г. Ачинск, ул. Красноярская", "description": "Любимое место отдыха горожан", "latitude": 56.2701, "longitude": 90.5012, "is_accessible": True},
        {"name": "Храм Покрова Пресвятой Богородицы", "address": "г. Ачинск, ул. Красный Партизан, 35", "description": "Православный храм начала XX века", "latitude": 56.2634, "longitude": 90.4891, "is_accessible": False},
        {"name": "Памятник воинам-ачинцам", "address": "г. Ачинск, пл. Ленина", "description": "Мемориал в честь героев Великой Отечественной войны", "latitude": 56.2670, "longitude": 90.4980, "is_accessible": True},
        {"name": "Городской фонтан", "address": "г. Ачинск, пр. Мира", "description": "Центральная достопримечательность с вечерней подсветкой", "latitude": 56.2665, "longitude": 90.4975, "is_accessible": True},
    ],
    "accommodations": [
        {"name": "Гостиница «Ачинск»", "address": "г. Ачинск, ул. Советская, 15", "description": "Центральная гостиница города", "price_per_night": 2500, "rating": 4.2, "latitude": 56.2680, "longitude": 90.4990},
        {"name": "Мини-отель «Уют»", "address": "г. Ачинск, пер. Больничный, 3", "description": "Тихий отель в спальном районе", "price_per_night": 1800, "rating": 3.8, "latitude": 56.2620, "longitude": 90.4850},
        {"name": "Хостел «Путник»", "address": "г. Ачинск, ул. Железнодорожная, 10", "description": "Бюджетное размещение рядом с вокзалом", "price_per_night": 900, "rating": 3.5, "latitude": 56.2710, "longitude": 90.5100},
        {"name": "Апартаменты «Дом на Мира»", "address": "г. Ачинск, пр. Мира, 45", "description": "Квартиры посуточно с кухней", "price_per_night": 2200, "rating": 4.5, "latitude": 56.2690, "longitude": 90.5020},
        {"name": "Гостевой дом «Таёжный»", "address": "г. Ачинск, ул. Лесная, 7", "description": "Уютный дом с баней и парковкой", "price_per_night": 3000, "rating": 4.7, "latitude": 56.2580, "longitude": 90.4780},
    ],
    "foods": [
        {"name": "Кафе «Сибирь»", "address": "г. Ачинск, пр. Мира, 30", "description": "Домашняя кухня, сибирские пельмени", "cuisine": "Русская", "avg_price": 800, "rating": 4.3, "phone": "+7 (39151) 2-34-56"},
        {"name": "Пиццерия «Италия»", "address": "г. Ачинск, ул. Красный Партизан, 12", "description": "Свежая пицца из дровяной печи", "cuisine": "Итальянская", "avg_price": 1200, "rating": 4.5, "phone": "+7 (39151) 3-45-67"},
        {"name": "Столовая «Домашняя»", "address": "г. Ачинск, ул. Советская, 8", "description": "Бизнес-ланчи и комплексные обеды", "cuisine": "Европейская", "avg_price": 400, "rating": 3.9, "phone": "+7 (39151) 1-23-45"},
        {"name": "Суши-бар «Сакура»", "address": "г. Ачинск, ТРЦ «Город», 2 этаж", "description": "Роллы, вок-лапша, азиатские закуски", "cuisine": "Азиатская", "avg_price": 1500, "rating": 4.1, "phone": "+7 (39151) 4-56-78"},
        {"name": "Кофейня «Уголок»", "address": "г. Ачинск, ул. Ленина, 5", "description": "Авторский кофе и десерты ручной работы", "cuisine": "Кофейня", "avg_price": 350, "rating": 4.6, "phone": "+7 (39151) 5-67-89"},
    ],
    "events": [
        {"title": "День города Ачинск", "description": "Праздничные мероприятия, концерт, фейерверк", "category": "Фестиваль", "event_date": "14.05.2026", "location": "пл. Ленина"},
        {"title": "Выставка местных художников", "description": "Картины, фотографии, скульптуры ачинских мастеров", "category": "Выставка", "event_date": "20.04.2026", "location": "Краеведческий музей"},
        {"title": "Концерт «Звёзды Сибири»", "description": "Выступление популярных сибирских исполнителей", "category": "Концерт", "event_date": "10.06.2026", "location": "ДК «Металлург»"},
        {"title": "Детский праздник «В гостях у сказки»", "description": "Аниматоры, игры, конкурсы для детей 3-10 лет", "category": "Детям", "event_date": "30.06.2027", "location": "Парк культуры и отдыха"},
        {"title": "Футбольный турнир «Кубок Ачинска»", "description": "Соревнования среди любительских команд", "category": "Спорт", "event_date": "10.09.2026", "location": "Стадион «Металлург»"},
    ],
    "souvenirs": [
        {"name": "Магнит «Ачинск»", "description": "Сувенирный магнит с видом города", "producer": "Мастерская «Сувениры Сибири»", "price": 150},
        {"name": "Кедровый бальзам", "description": "Натуральный бальзам на кедровых орешках, 100 мл", "producer": "ООО «Таёжные дары»", "price": 450},
        {"name": "Набор открыток «Ачинск исторический»", "description": "10 старинных фотографий города в конверте", "producer": "Краеведческий музей", "price": 300},
        {"name": "Вязаные варежки с оленями", "description": "Ручная работа, шерсть, размер универсальный", "producer": "Мастер Елена К.", "price": 800},
        {"name": "Чайный сбор «Сибирский»", "description": "Травяной сбор с чабрецом, зверобоем, душицей", "producer": "ИП Петрова А.В.", "price": 250},
    ],
    "safety": [
        {"name": "Полиция (дежурная часть)", "category": "Полиция", "phone": "02", "address": "г. Ачинск, ул. Советская, 25", "latitude": 56.2690, "longitude": 90.5000},
        {"name": "МЧС России (Ачинский отряд)", "category": "МЧС", "phone": "101", "address": "г. Ачинск, ул. Пожарная, 1", "latitude": 56.2600, "longitude": 90.4800},
        {"name": "Скорая медицинская помощь", "category": "Скорая помощь", "phone": "103", "address": "Выездная служба", "latitude": None, "longitude": None},
        {"name": "Городская больница №1", "category": "Медицина", "phone": "+7 (39151) 2-11-11", "address": "г. Ачинск, ул. Больничная, 10", "latitude": 56.2630, "longitude": 90.4920},
        {"name": "Аптека «36,6»", "category": "Аптека", "phone": "+7 (39151) 3-22-33", "address": "г. Ачинск, пр. Мира, 15", "latitude": 56.2670, "longitude": 90.4970},
    ],
    "routes": [
        {"title": "Пешая прогулка по центру", "description": "Маршрут по главным достопримечательностям исторического центра", "transport_type": "Пешком", "difficulty": "Лёгкий", "duration_hours": 2.5},
        {"title": "Ачинск за один день", "description": "Обзорный маршрут на автомобиле: музеи, храмы, парки", "transport_type": "Автомобиль", "difficulty": "Средний", "duration_hours": 6},
        {"title": "Храмы Ачинска", "description": "Паломнический маршрут по православным святыням города", "transport_type": "Пешком", "difficulty": "Лёгкий", "duration_hours": 3},
        {"title": "Природные окрестности", "description": "Выездной маршрут к живописным местам за городом", "transport_type": "Автомобиль", "difficulty": "Средний", "duration_hours": 5},
        {"title": "Семейный маршрут с детьми", "description": "Парки, фонтаны, игровые площадки — всё для отдыха с ребёнком", "transport_type": "Пешком", "difficulty": "Лёгкий", "duration_hours": 4},
    ],
    "postcards": [
        {"title": "Вид на центр с высоты", "image_url": "/static/images/postcards/center_view.jpg", "description": "Панорама проспекта Мира"},
        {"title": "Храм Покрова Богородицы", "image_url": "/static/images/postcards/church.jpg", "description": "Архитектурная жемчужина Ачинска"},
        {"title": "Зимний Ачинск", "image_url": "/static/images/postcards/winter.jpg", "description": "Снежный город в новогодних огнях"},
        {"title": "Река Чулым", "image_url": "/static/images/postcards/river.jpg", "description": "Природная красота сибирской реки"},
        {"title": "Памятник воинам", "image_url": "/static/images/postcards/memorial.jpg", "description": "Вечная память героям"},
    ],
}


async def seed_database():
    """Заполнение базы тестовыми данными"""
    async with async_session_maker() as session:
        
        # Достопримечательности
        for item in TEST_DATA["attractions"]:
            obj = Attraction(**item, is_active=True)
            session.add(obj)
        
        # Гостиницы
        for item in TEST_DATA["accommodations"]:
            obj = Accommodation(**item, is_active=True)
            session.add(obj)
        
        # Рестораны
        for item in TEST_DATA["foods"]:
            obj = Food(**item, is_active=True)
            session.add(obj)
        
        # События
        for item in TEST_DATA["events"]:
            obj = Event(**item, is_active=True)
            session.add(obj)
        
        # Сувениры
        for item in TEST_DATA["souvenirs"]:
            obj = Souvenir(**item, is_active=True)
            session.add(obj)
        
        # Безопасность
        for item in TEST_DATA["safety"]:
            obj = SafetyObject(**item, is_active=True)
            session.add(obj)
        
        # Маршруты
        for item in TEST_DATA["routes"]:
            obj = Route(**item, is_active=True)
            session.add(obj)
        
        # Открытки
        for item in TEST_DATA["postcards"]:
            obj = PostcardTemplate(**item, is_active=True)
            session.add(obj)
        
        await session.commit()
        print("✅ Тестовые данные успешно добавлены!")


if __name__ == "__main__":
    asyncio.run(seed_database())