import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from models import (Accommodation, Attraction, Event, Food, PostcardTemplate,
                    Route, SafetyMemo, SafetyObject, Souvenir, User)
from security import get_password_hash


async def create_test_accommodation(session: AsyncSession, **kwargs):
    """Создаёт тестовое размещение"""
    defaults = {
        "name": "Тест Гостиница",
        "address": "ул. Тестовая, 1",
        "is_active": True,
    }
    defaults.update(kwargs)
    obj = Accommodation(**defaults)
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj


async def create_test_attraction(session: AsyncSession, **kwargs):
    """Создаёт тестовую достопримечательность"""
    defaults = {
        "name": "Тест Достопримечательность",
        "description": "Описание",
        "is_active": True,
    }
    defaults.update(kwargs)
    obj = Attraction(**defaults)
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj


async def create_test_event(session: AsyncSession, **kwargs):
    """Создаёт тестовое событие"""
    from datetime import datetime, timedelta

    defaults = {
        "title": "Тест Событие",
        "location": "Ачинск",
        "event_date": datetime.now() + timedelta(days=10),
        "is_active": True,
    }
    defaults.update(kwargs)
    obj = Event(**defaults)
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj


async def create_test_food(session: AsyncSession, **kwargs):
    """Создаёт тестовое заведение питания"""
    defaults = {
        "name": "Тест Заведение",
        "address": "ул. Тестовая, 1",
        "is_active": True,
    }
    defaults.update(kwargs)
    obj = Food(**defaults)
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj


async def create_test_postcard(session: AsyncSession, **kwargs):
    """Создаёт тестовый шаблон открытки

    Примечание: В модели поле называется 'title', а не 'name'
    """
    defaults = {
        "title": "Тест Открытка",
        "image_url": "/static/images/test.jpg",
        "is_active": True,
    }
    defaults.update(kwargs)
    obj = PostcardTemplate(**defaults)
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj


async def create_test_route(session: AsyncSession, **kwargs):
    """Создаёт тестовый маршрут"""
    defaults = {"title": "Тест Маршрут", "duration_hours": 2.0, "is_active": True}
    defaults.update(kwargs)
    obj = Route(**defaults)
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj


async def create_test_safety_object(session: AsyncSession, **kwargs):
    """Создаёт тестовый объект безопасности

    Примечание: Поле 'phone' обязательно (nullable=False в модели)
    """
    defaults = {
        "name": "Тест Объект",
        "category": "Медицина",
        "address": "ул. Тестовая, 1",
        "phone": "+70000000000",  # Обязательно!
        "is_active": True,
    }
    defaults.update(kwargs)
    obj = SafetyObject(**defaults)
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj


async def create_test_safety_memo(session: AsyncSession, **kwargs):
    """Создаёт тестовую памятку безопасности"""
    defaults = {
        "title": "Тест Памятка",
        "content": "Текст",
        "order": 1,
        "is_active": True,
    }
    defaults.update(kwargs)
    obj = SafetyMemo(**defaults)
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj


async def create_test_souvenir(session: AsyncSession, **kwargs):
    """Создаёт тестовый сувенирный магазин

    Примечание: Поля 'price' и 'producer' удалены, так как их нет в модели Souvenir
    """
    defaults = {
        "name": "Тест Сувенир",
        "description": "Описание",
        "address": "ул. Тестовая, 1",
        "category": "Сувениры",
        "is_active": True,
    }
    defaults.update(kwargs)
    obj = Souvenir(**defaults)
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj


async def create_test_user(session: AsyncSession, **kwargs):
    """Создаёт тестового пользователя"""
    defaults = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "TestPass123!",
        "is_approved": True,  # Важно для успешного входа в тестах
    }
    defaults.update(kwargs)
    hashed = get_password_hash(defaults.pop("password"))
    obj = User(hashed_password=hashed, **defaults)
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj


async def authenticate_user(client: AsyncClient, username: str, password: str) -> str:
    """Авторизует пользователя и возвращает access_token

    Примечание: Использует /api/auth/token (стандарт OAuth2), а не /api/auth/login
    """
    response = await client.post(
        "/api/auth/token", data={"username": username, "password": password}
    )
    assert response.status_code == 200, f"Login failed: {response.text}"
    return response.json()["access_token"]


def assert_response_ok(response):
    """Проверяет, что ответ имеет статус 200"""
    assert (
        response.status_code == 200
    ), f"Expected 200, got {response.status_code}: {response.text}"


def assert_response_not_found(response):
    """Проверяет, что ответ имеет статус 404"""
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"


def assert_response_unauthorized(response):
    """Проверяет, что ответ имеет статус 401"""
    assert response.status_code == 401, f"Expected 401, got {response.status_code}"


def assert_response_created(response):
    """Проверяет, что ответ имеет статус 201"""
    assert response.status_code == 201, f"Expected 201, got {response.status_code}"
