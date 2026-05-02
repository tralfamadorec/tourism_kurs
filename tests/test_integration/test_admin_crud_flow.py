import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession  # ← Добавлен импорт

from tests.utils import (assert_response_ok, authenticate_user,
                         create_test_attraction, create_test_user)


@pytest.mark.asyncio
async def test_admin_crud_attractions_flow(
    client: AsyncClient, test_session: AsyncSession, test_admin_data: dict
):
    # Создаём утверждённого админа напрямую, минуя API-регистрацию
    from security import create_access_token

    admin = await create_test_user(
        test_session, **test_admin_data, is_approved=True  # ← Важно: сразу утверждаем
    )

    # Создаём токен напрямую
    token = create_access_token(data={"sub": admin.username, "role": admin.role})

    headers = {"Authorization": f"Bearer {token}"}

    # 1. Создаём достопримечательность
    new_data = {
        "name": "Тестовая достопримечательность",
        "description": "Описание для теста",
        "address": "ул. Тестовая, 1",
    }
    create_resp = await client.post("/api/attractions/", json=new_data, headers=headers)
    assert create_resp.status_code == 201
    created = create_resp.json()
    assert created["name"] == new_data["name"]

    # 2. Получаем созданную достопримечательность
    get_resp = await client.get(f"/api/attractions/{created['id']}", headers=headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["name"] == new_data["name"]

    # 3. Обновляем достопримечательность
    update_data = {"description": "Обновлённое описание"}
    update_resp = await client.put(
        f"/api/attractions/{created['id']}", json=update_data, headers=headers
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["description"] == update_data["description"]

    # 4. Удаляем достопримечательность
    delete_resp = await client.delete(
        f"/api/attractions/{created['id']}", headers=headers
    )
    assert delete_resp.status_code == 200

    # 5. Проверяем, что достопримечательность удалена
    not_found_resp = await client.get(f"/api/attractions/{created['id']}")
    assert not_found_resp.status_code == 404
