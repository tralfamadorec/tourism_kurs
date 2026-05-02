import asyncio
import os
import sys

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from slowapi import Limiter
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker, create_async_engine)
from sqlalchemy.pool import NullPool

from config import settings
from database import Base, get_db
from main import app

from tests.utils import create_test_user

# Добавляем корень проекта в PYTHONPATH для корректных импортов
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Тестовая БД
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    settings.DATABASE_URL.replace("achinsk_tourism", "achinsk_tourism_test"),
)


# ИСПРАВЛЕНИЕ 1: Изменили scope на "function" для совместимости с pytest-asyncio
@pytest_asyncio.fixture(scope="function")
async def test_engine():
    """Создаёт асинхронный движок для тестовой БД"""
    engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    # async with engine.begin() as conn:
    # await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_session(test_engine):
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        # Уберите autocommit=True, если он есть
    )

    async with async_session() as session:
        for table in reversed(Base.metadata.sorted_tables):
            await session.execute(table.delete())
        await session.commit()
        yield session
        await session.close()


@pytest.fixture
def override_get_db(test_session):
    """Переопределяет зависимость get_db для использования тестовой сессии"""

    async def _get_db():
        yield test_session

    return _get_db


@pytest_asyncio.fixture(scope="function")
async def client(override_get_db):
    """Асинхронный клиент для тестов API"""
    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def sync_client(override_get_db):
    """Синхронный клиент для тестов страниц"""
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data():
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "SecurePass123!",
        "role": "user",
    }


@pytest.fixture
def test_admin_data():
    return {
        "username": "testadmin",
        "email": "admin@example.com",
        "password": "AdminPass123!",
        "role": "admin",
    }


# tests/conftest.py — добавьте в конец файла

# tests/test_api/test_auth.py
import asyncio  # ← убедитесь, что импорт есть


@pytest.mark.asyncio
async def test_login_not_approved_user(
    client: AsyncClient, test_session, test_user_data: dict
):
    """Проверяет отказ во входе для неутверждённого пользователя"""
    # 🔹 Пауза, чтобы избежать срабатывания rate limiter (5/minute)
    await asyncio.sleep(1.0)

    await create_test_user(
        test_session, **test_user_data, is_approved=False, is_active=True
    )

    response = await client.post(
        "/api/auth/token",
        data={
            "username": test_user_data["username"],
            "password": test_user_data["password"],
        },
    )
    assert response.status_code == 403
    assert "подтверждения" in response.json()["detail"].lower()


# tests/conftest.py — добавить в самый конец файла


@pytest.fixture(autouse=True, scope="function")
def disable_rate_limiter_in_tests(monkeypatch):
    """
    Отключает применение rate limits в тестах,
    заменяя метод проверки лимита на заглушку.
    """
    from slowapi.extension import Limiter

    # Мокаем метод _check_request_limit, чтобы он всегда пропускал запросы
    def mock_check_limit(*args, **kwargs):
        return True

    # Применяем мок ко всем экземплярам лимитера
    monkeypatch.setattr(Limiter, "_check_request_limit", mock_check_limit)


# tests/conftest.py — добавьте в конец файла, ПОСЛЕ всех остальных фикстур


@pytest.fixture(autouse=True, scope="session")
def disable_slowapi_middleware_in_tests():
    """
    Отключает SlowAPIMiddleware в тестах, чтобы избежать
    ошибки 'State' object has no attribute 'view_rate_limit'.
    Rate limiting при этом остаётся рабочим в продакшене.
    """
    from main import app

    # Сохраняем оригинальный стек мидлварей
    original_middleware = app.user_middleware[:]
    original_middleware_stack = app.middleware_stack

    # Фильтруем только SlowAPIMiddleware
    from slowapi.middleware import SlowAPIMiddleware

    app.user_middleware = [m for m in app.user_middleware if m.cls != SlowAPIMiddleware]

    # Пересобираем стек мидлварей
    app.middleware_stack = app.build_middleware_stack()

    yield

    # Восстанавливаем после тестов
    app.user_middleware = original_middleware
    app.middleware_stack = original_middleware_stack


# tests/conftest.py — добавьте ЭТУ фикстуру в конец файла, ПОСЛЕ всех остальных


@pytest.fixture(autouse=True, scope="session")
def disable_slowapi_headers_injection():
    """
    Отключает инъекцию заголовков rate limit в тестах,
    чтобы избежать ошибки 'State' object has no attribute 'view_rate_limit'.
    """
    from unittest.mock import MagicMock

    from slowapi.extension import Limiter

    # Сохраняем оригинальный метод
    original_inject = Limiter._inject_headers

    # Заменяем на заглушку, которая просто возвращает response
    def mock_inject_headers(response, view_rate_limit):
        return response

    Limiter._inject_headers = mock_inject_headers

    yield

    # Восстанавливаем после тестов
    Limiter._inject_headers = original_inject


@pytest.fixture(autouse=True, scope="session")
def mock_slowapi_view_rate_limit():
    """
    Мокает доступ к request.state.view_rate_limit в slowapi,
    чтобы избежать ошибки в тестах с httpx.AsyncClient.
    """
    from unittest.mock import MagicMock, patch

    from slowapi.extension import _rate_limit_exceeded_handler

    # Мокаем атрибут, который вызывает ошибку
    with patch(
        "slowapi.extension.Limiter._inject_headers", return_value=lambda r, v: r
    ):
        yield


@pytest.fixture(autouse=True)
def mock_slowapi_state(monkeypatch):
    """Автоматически фиксит slowapi view_rate_limit для ВСЕХ тестов"""

    def mock_state_getattr(self, name):
        if name == "view_rate_limit":
            return None  # slowapi ожидает объект или None
        raise AttributeError(f"'State' object has no attribute '{name}'")

    monkeypatch.setattr(
        "starlette.datastructures.State.__getattr__", mock_state_getattr
    )
