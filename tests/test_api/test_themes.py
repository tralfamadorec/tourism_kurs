# tests/test_api/test_themes.py
import pytest
from httpx import AsyncClient

from security import create_access_token
from tests.utils import assert_response_ok, create_test_user


@pytest.mark.asyncio
async def test_get_active_theme_default(client: AsyncClient):
    """Проверка получения активной темы по умолчанию (когда настройка не существует)"""
    response = await client.get("/themes/active")
    assert response.status_code == 200
    data = response.json()
    assert data["active_theme"] == "default"


@pytest.mark.asyncio
async def test_get_active_theme_custom(client: AsyncClient, test_session):
    """Проверка получения установленной активной темы"""
    from models import SiteSetting

    # Создаём настройку темы напрямую в БД
    setting = SiteSetting(key="active_theme", value="dark")
    test_session.add(setting)
    await test_session.commit()

    response = await client.get("/themes/active")
    assert response.status_code == 200
    data = response.json()
    assert data["active_theme"] == "dark"


@pytest.mark.asyncio
async def test_set_active_theme_unauthorized(client: AsyncClient):
    """Проверка отказа в установке темы без авторизации"""
    response = await client.patch("/themes/active", json={"active_theme": "dark"})
    assert response.status_code == 401  # или 403, зависит от реализации


@pytest.mark.asyncio
async def test_set_active_theme_regular_user_denied(client: AsyncClient, test_session):
    """Проверка отказа в установке темы для обычного пользователя (не админ)"""
    # Создаём обычного пользователя
    user = await create_test_user(
        test_session,
        username="regular_user",
        email="regular@test.com",
        password="Pass123!",
        role="user",  # ← не admin/super_admin
        is_approved=True,
    )

    token = create_access_token(data={"sub": user.username, "role": user.role})
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.patch(
        "/themes/active", json={"active_theme": "dark"}, headers=headers
    )
    # Ожидаем 403, так как роль не подходит
    assert response.status_code == 403
    assert (
        "доступ" in response.json()["detail"].lower()
        or "роль" in response.json()["detail"].lower()
    )


@pytest.mark.asyncio
async def test_set_active_theme_admin_success(client: AsyncClient, test_session):
    """Проверка успешной установки темы администратором"""
    # Создаём администратора
    admin = await create_test_user(
        test_session,
        username="theme_admin",
        email="admin@test.com",
        password="AdminPass123!",
        role="admin",  # ← подходящая роль
        is_approved=True,
    )

    token = create_access_token(data={"sub": admin.username, "role": admin.role})
    headers = {"Authorization": f"Bearer {token}"}

    # Устанавливаем тему
    response = await client.patch(
        "/themes/active", json={"active_theme": "dark"}, headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["active_theme"] == "dark"

    # Проверяем, что тема действительно сохранилась
    get_response = await client.get("/themes/active")
    assert get_response.status_code == 200
    assert get_response.json()["active_theme"] == "dark"


@pytest.mark.asyncio
async def test_set_active_theme_super_admin_success(client: AsyncClient, test_session):
    """Проверка успешной установки темы super_admin"""
    # Создаём super_admin
    super_admin = await create_test_user(
        test_session,
        username="super_admin",
        email="super@test.com",
        password="SuperPass123!",
        role="super_admin",
        is_approved=True,
    )

    token = create_access_token(
        data={"sub": super_admin.username, "role": super_admin.role}
    )
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.patch(
        "/themes/active", json={"active_theme": "light"}, headers=headers
    )
    assert response.status_code == 200
    assert response.json()["active_theme"] == "light"


@pytest.mark.asyncio
async def test_set_active_theme_invalid_payload(client: AsyncClient, test_session):
    """Проверка обработки невалидного запроса на установку темы"""
    admin = await create_test_user(
        test_session,
        username="valid_admin",
        email="valid@test.com",
        password="Pass123!",
        role="admin",
        is_approved=True,
    )

    token = create_access_token(data={"sub": admin.username, "role": admin.role})
    headers = {"Authorization": f"Bearer {token}"}

    # Пустой JSON
    response = await client.patch("/themes/active", json={}, headers=headers)
    assert response.status_code in [400, 422]  # Bad Request или Validation Error

    # Неверный тип поля
    response = await client.patch(
        "/themes/active",
        json={"active_theme": 123},  # должно быть строкой
        headers=headers,
    )
    assert response.status_code in [400, 422]
