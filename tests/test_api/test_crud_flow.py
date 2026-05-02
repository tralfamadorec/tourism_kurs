# tests/test_api/test_crud_flows.py
import pytest
from httpx import AsyncClient

from security import create_access_token
from tests.utils import (create_test_attraction, create_test_event,
                         create_test_user)


# tests/test_api/test_crud_flow.py
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "endpoint, create_data, update_data, model_factory",
    [
        (
            "/api/attractions/",
            {"name": "Тест Парк", "description": "Описание"},
            {"description": "Обновлено"},
            create_test_attraction,
        ),
        (
            "/api/events/",
            {
                "title": "Тест Событие",
                "location": "Ачинск",
                "is_recurring": False,
            },  # ← Явно задаём
            {"location": "Новое место"},
            lambda s, **kw: create_test_event(s, **kw),
        ),
    ],
)
async def test_crud_flow_for_routes(
    client: AsyncClient,
    test_session,
    endpoint: str,
    create_data: dict,
    update_data: dict,
    model_factory,
):
    """Универсальный тест CRUD для ключевых маршрутов"""
    # Создаём админа для доступа к POST/PUT/DELETE
    admin = await create_test_user(
        test_session,
        username="crud_admin",
        email="crud@t.com",
        password="Pass123!",
        role="admin",
        is_approved=True,
    )
    token = create_access_token(data={"sub": admin.username, "role": admin.role})
    headers = {"Authorization": f"Bearer {token}"}

    # 1. CREATE
    resp = await client.post(endpoint, json=create_data, headers=headers)
    assert resp.status_code == 201
    item_id = resp.json()["id"]

    # 2. READ
    resp = await client.get(f"{endpoint}{item_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == item_id

    # 3. UPDATE
    resp = await client.put(f"{endpoint}{item_id}", json=update_data, headers=headers)
    assert resp.status_code == 200
    for k, v in update_data.items():
        assert resp.json()[k] == v

    # 4. DELETE (soft delete)
    resp = await client.delete(f"{endpoint}{item_id}", headers=headers)
    assert resp.status_code == 200

    # 5. VERIFY DELETED
    resp = await client.get(f"{endpoint}{item_id}")
    assert resp.status_code == 404
