import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession  # ← Добавлен импорт

from tests.utils import (assert_response_ok, create_test_attraction,
                         create_test_user)


@pytest.mark.asyncio
async def test_complete_user_journey(
    client: AsyncClient, test_session: AsyncSession, test_user_data: dict
):
    from security import create_access_token

    # Создаём утверждённого пользователя и тестовые данные
    user = await create_test_user(test_session, **test_user_data, is_approved=True)
    await create_test_attraction(
        test_session, name="Парк Троицкий", description="Зелёная зона"
    )

    # Создаём токен напрямую
    token = create_access_token(data={"sub": user.username, "role": user.role})
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Проверяем публичные страницы
    public_resp = await client.get("/attractions")
    assert public_resp.status_code == 200

    # 2. Проверяем поиск через API
    search_resp = await client.get("/api/attractions/?search=парк")
    assert search_resp.status_code == 200
    assert len(search_resp.json()) >= 1

    # 3. Проверяем доступ к защищённому эндпоинту
    me_resp = await client.get("/api/auth/me", headers=headers)
    assert me_resp.status_code == 200
    assert me_resp.json()["username"] == test_user_data["username"]

    # 4. Проверяем создание объекта (если эндпоинт реализован)
    # (опционально, если бэкенд поддерживает создание через API)
