# tests/test_api/test_admin_users.py
import pytest
from httpx import AsyncClient

from tests.utils import create_test_user


# tests/test_api/test_admin_users.py
@pytest.mark.asyncio
async def test_admin_get_users_and_change_role(
    client: AsyncClient, test_session, test_admin_data: dict
):
    # 🔹 ИСПРАВЛЕНО: объединяем данные без конфликта ключей
    admin_payload = {**test_admin_data, "role": "super_admin", "is_approved": True}
    super_admin = await create_test_user(test_session, **admin_payload)

    from security import create_access_token

    token = create_access_token(
        data={"sub": super_admin.username, "role": super_admin.role}
    )
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Получаем список пользователей
    resp = await client.get("/api/admin/users/", headers=headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

    # 2. Создаём обычного пользователя и меняем ему роль
    regular = await create_test_user(
        test_session,
        username="temp_user",
        email="temp@test.com",
        password="Pass123!",
        role="user",
        is_approved=True,
    )
    resp = await client.patch(
        f"/api/admin/users/{regular.id}",
        json={"role": "admin", "is_approved": True},
        headers=headers,
    )
    assert resp.status_code == 200
    assert resp.json()["role"] == "admin"


# tests/test_api/test_admin_users.py
@pytest.mark.asyncio
async def test_reset_user_password(
    client: AsyncClient, test_session, test_admin_data: dict
):
    """Покрытие POST /api/admin/users/{id}/reset-password"""
    from security import create_access_token

    # 🔹 ИСПРАВЛЕНО: объединяем словарь, чтобы явно переопределить role
    admin_payload = {**test_admin_data, "role": "super_admin", "is_approved": True}
    super_admin = await create_test_user(test_session, **admin_payload)

    token = create_access_token(
        data={"sub": super_admin.username, "role": super_admin.role}
    )
    headers = {"Authorization": f"Bearer {token}"}

    # Создаём обычного пользователя, которому сбросим пароль
    regular_user = await create_test_user(
        test_session,
        username="user_to_reset",
        email="reset@test.com",
        password="OldPass123!",
        is_approved=True,
    )

    response = await client.post(
        f"/api/admin/users/{regular_user.id}/reset-password",
        json={"new_password": "NewSecurePass456!"},
        headers=headers,
    )

    assert response.status_code == 200
    assert "пароль успешно сброшен" in response.json()["message"].lower()


# tests/test_api/test_admin_users.py


@pytest.mark.asyncio
async def test_delete_user_by_super_admin(
    client: AsyncClient, test_session, test_admin_data: dict
):
    """Покрытие DELETE /api/admin/users/{id}"""
    from security import create_access_token

    # Создаем super_admin
    admin_payload = {**test_admin_data, "role": "super_admin", "is_approved": True}
    super_admin = await create_test_user(test_session, **admin_payload)

    token = create_access_token(
        data={"sub": super_admin.username, "role": super_admin.role}
    )
    headers = {"Authorization": f"Bearer {token}"}

    # Создаем пользователя для удаления
    user_to_delete = await create_test_user(
        test_session,
        username="user_to_delete",
        email="del@test.com",
        password="Pass123!",
        is_approved=True,
    )

    # Удаляем
    response = await client.delete(
        f"/api/admin/users/{user_to_delete.id}", headers=headers
    )

    # Проверяем статус (обычно 204 No Content или 200 OK)
    assert response.status_code in [200, 204]

    # Проверяем, что пользователя больше нет в базе
    from sqlalchemy import select

    from models import User

    result = await test_session.execute(
        select(User).where(User.id == user_to_delete.id)
    )
    assert result.scalar_one_or_none() is None


# tests/test_api/test_admin_users.py
@pytest.mark.asyncio
async def test_delete_user_success(
    client: AsyncClient, test_session, test_admin_data: dict
):
    """Покрытие DELETE /api/admin/users/{id}"""
    from security import create_access_token

    # Создаём super_admin
    admin_payload = {**test_admin_data, "role": "super_admin", "is_approved": True}
    super_admin = await create_test_user(test_session, **admin_payload)
    token = create_access_token(
        data={"sub": super_admin.username, "role": super_admin.role}
    )
    headers = {"Authorization": f"Bearer {token}"}

    # Создаём обычного пользователя для удаления
    user_to_delete = await create_test_user(
        test_session,
        username="to_delete",
        email="del@t.com",
        password="Pass123!",
        is_approved=True,
    )

    response = await client.delete(
        f"/api/admin/users/{user_to_delete.id}", headers=headers
    )
    assert response.status_code == 204  # или 200, зависит от реализации

    # Проверяем, что пользователя действительно нет в БД
    from sqlalchemy import select

    from models import User

    result = await test_session.execute(
        select(User).where(User.id == user_to_delete.id)
    )
    assert result.scalar_one_or_none() is None
