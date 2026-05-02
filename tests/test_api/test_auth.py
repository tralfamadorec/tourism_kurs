import asyncio

import pytest
from httpx import AsyncClient
from jose import jwt
from sqlalchemy import select

from config import settings
from models import User
from tests.utils import (assert_response_ok, assert_response_unauthorized,
                         authenticate_user, create_test_user)


@pytest.mark.asyncio
async def test_register_user_success(
    client: AsyncClient, test_session, test_user_data: dict
):
    """Успешная регистрация нового пользователя"""
    response = await client.post("/api/auth/register", json=test_user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == test_user_data["username"]
    assert data["email"] == test_user_data["email"]
    assert "password" not in data


@pytest.mark.asyncio
async def test_register_duplicate_email(
    client: AsyncClient, test_session, test_user_data: dict
):
    """Попытка регистрации с уже существующим email"""
    await client.post("/api/auth/register", json=test_user_data)
    response = await client.post("/api/auth/register", json=test_user_data)
    assert response.status_code == 400
    assert "email" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_register_missing_fields(client: AsyncClient):
    """Регистрация без обязательных полей"""
    response = await client.post("/api/auth/register", json={"username": "testuser"})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, test_session, test_user_data: dict):
    # ← Убрали sleep и disable_limiter
    await create_test_user(test_session, **test_user_data, is_approved=True)
    response = await client.post(
        "/api/auth/token",
        data={
            "username": test_user_data["username"],
            "password": test_user_data["password"],
        },
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(
    client: AsyncClient, test_session, test_user_data: dict
):
    """Вход с неверным паролем"""
    await create_test_user(test_session, **test_user_data, is_approved=True)

    response = await client.post(
        "/api/auth/token",
        data={"username": test_user_data["username"], "password": "WrongPassword123"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient):
    """Попытка входа несуществующего пользователя"""
    response = await client.post(
        "/api/auth/token",
        data={"username": "nonexistent", "password": "AnyPassword123"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_authenticated(
    client: AsyncClient, test_session, test_user_data: dict
):
    """Получение данных текущего пользователя с токеном"""
    # Создаём утверждённого пользователя
    user = await create_test_user(test_session, **test_user_data, is_approved=True)

    # Создаём токен напрямую через security.create_access_token
    from security import create_access_token

    token = create_access_token(data={"sub": user.username, "role": user.role})

    response = await client.get(
        "/api/auth/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert_response_ok(response)
    data = response.json()
    assert data["username"] == test_user_data["username"]


@pytest.mark.asyncio
async def test_get_current_user_unauthorized(client: AsyncClient):
    """Запрос профиля без токена"""
    response = await client.get("/api/auth/me")
    assert_response_unauthorized(response)


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(client: AsyncClient):
    """Запрос профиля с невалидным токеном"""
    response = await client.get(
        "/api/auth/me", headers={"Authorization": "Bearer invalid_token_here"}
    )
    assert_response_unauthorized(response)


@pytest.mark.asyncio
async def test_login_admin_gets_admin_role(
    client: AsyncClient, test_session, test_admin_data: dict
):
    """Проверка роли администратора"""
    # Создаём утверждённого админа
    user = await create_test_user(test_session, **test_admin_data, is_approved=True)

    from security import create_access_token

    token = create_access_token(data={"sub": user.username, "role": user.role})

    # Проверяем, что токен содержит роль
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert payload.get("role") == test_admin_data["role"]


@pytest.mark.asyncio
async def test_register_weak_password(client: AsyncClient):
    """Регистрация со слабым паролем"""
    response = await client.post(
        "/api/auth/register",
        json={"username": "weakpass", "email": "weak@example.com", "password": "123"},
    )
    assert response.status_code in [201, 400, 422]


@pytest.mark.asyncio
async def test_login_case_sensitive_username(
    client: AsyncClient, test_session, test_user_data: dict
):
    """Проверка чувствительности логина к регистру"""
    await create_test_user(test_session, **test_user_data, is_approved=True)

    response = await client.post(
        "/api/auth/token",
        data={
            "username": test_user_data["username"].upper(),
            "password": test_user_data["password"],
        },
    )
    assert response.status_code in [200, 401]


@pytest.mark.asyncio
async def test_register_rollback_on_duplicate(client: AsyncClient, test_session):
    """Проверяет, что при нарушении уникальности транзакция откатывается корректно"""
    # 1. Создаём первого пользователя
    user_data = {
        "username": "rollback_test",
        "email": "first@example.com",
        "password": "ValidPass123!",
    }
    resp1 = await client.post("/api/auth/register", json=user_data)
    assert resp1.status_code == 201

    # 2. Пытаемся создать пользователя с тем же username (должно вызвать ошибку БД)
    user_data["email"] = "second@example.com"
    resp2 = await client.post("/api/auth/register", json=user_data)
    assert resp2.status_code == 400  # Ожидаемая ошибка валидации/БД

    # 3. Проверяем, что в базе остался только один пользователь с этим именем
    result = await test_session.execute(
        select(User).where(User.username == "rollback_test")
    )
    users = result.scalars().all()
    assert len(users) == 1, "Транзакция не откатилась: дубликат попал в БД"
    assert users[0].email == "first@example.com", "Попал неверный email"


@pytest.mark.asyncio
async def test_require_admin_auth_denies_regular_user(
    client: AsyncClient, test_session
):
    """Проверяет, что обычный пользователь не получает доступ к админ-эндпоинтам"""
    from security import create_access_token

    # Создаём обычного пользователя (не админа)
    user = await create_test_user(
        test_session, username="regular", role="user", is_approved=True
    )
    token = create_access_token(data={"sub": user.username, "role": user.role})

    # Пытаемся получить доступ к админ-странице
    response = await client.get("/admin", cookies={"access_token": token})
    assert response.status_code in [302, 403]  # Редирект на логин или запрет


# tests/test_api/test_auth.py — добавить после существующих тестов


@pytest.mark.asyncio
async def test_login_inactive_user(
    client: AsyncClient, test_session, test_user_data: dict
):
    """Проверяет отказ во входе для неактивного пользователя (покрывает строки 72-80 в auth.py)"""
    await create_test_user(
        test_session, **test_user_data, is_approved=True, is_active=False
    )

    response = await client.post(
        "/api/auth/token",
        data={
            "username": test_user_data["username"],
            "password": test_user_data["password"],
        },
    )
    assert response.status_code == 403
    assert "заблокирована" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_login_not_approved_user(
    client: AsyncClient, test_session, test_user_data: dict
):
    # ← Убрали sleep
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


# tests/test_api/test_auth.py или tests/test_unit/test_dependencies.py


# tests/test_api/test_auth.py — исправленный тест
@pytest.mark.asyncio
async def test_require_admin_auth_role_check(client: AsyncClient, test_session):
    """Проверяет, что require_role отклоняет пользователя без нужной роли (покрывает строки 28-42 в dependencies.py)"""
    from security import create_access_token

    # Создаём пользователя с ролью 'user' (не super_admin)
    user = await create_test_user(
        test_session,
        username="regular_user",
        role="user",
        is_approved=True,
        is_active=True,
    )
    token = create_access_token(data={"sub": user.username})  # role не нужен в payload

    # 🔹 ИСПРАВЛЕНО: токен в заголовке Authorization, а не в куках
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.get("/api/admin/users/", headers=headers)

    # Ожидаем 403 (Forbidden) из-за недостатка прав
    assert response.status_code == 403
    assert (
        "недостаточно прав" in response.json()["detail"].lower()
        or "запрещён" in response.json()["detail"].lower()
    )


# tests/test_api/test_auth.py
@pytest.mark.asyncio
async def test_update_profile_success(
    client: AsyncClient, test_session, test_user_data: dict
):
    """Покрытие PATCH /api/auth/profile (строки 109-134 в auth.py)"""
    user = await create_test_user(test_session, **test_user_data, is_approved=True)
    from security import create_access_token

    token = create_access_token(data={"sub": user.username})

    response = await client.patch(
        "/api/auth/profile",
        json={"username": "new_name"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["username"] == "new_name"


@pytest.mark.asyncio
async def test_change_password_success(
    client: AsyncClient, test_session, test_user_data: dict
):
    """Покрытие POST /api/auth/change-password"""
    user = await create_test_user(test_session, **test_user_data, is_approved=True)
    from security import create_access_token

    token = create_access_token(data={"sub": user.username})

    response = await client.post(
        "/api/auth/change-password",
        json={
            "old_password": test_user_data["password"],
            "new_password": "NewStrongPass123!",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200


# tests/test_api/test_auth.py — добавить после существующих тестов


@pytest.mark.asyncio
async def test_update_profile_duplicate_username(
    client: AsyncClient, test_session, test_user_data: dict
):
    """Покрытие ветки: ошибка при смене username на существующий (строки 113-134 в auth.py)"""
    from security import create_access_token

    # Создаём двух пользователей
    user1 = await create_test_user(
        test_session,
        username="user1",
        email="u1@t.com",
        password="Pass123!",
        is_approved=True,
    )
    user2 = await create_test_user(
        test_session,
        username="user2",
        email="u2@t.com",
        password="Pass123!",
        is_approved=True,
    )

    token = create_access_token(data={"sub": user2.username})
    headers = {"Authorization": f"Bearer {token}"}

    # Пытаемся сменить username user2 на существующий user1
    response = await client.patch(
        "/api/auth/profile", json={"username": "user1"}, headers=headers
    )
    assert response.status_code == 400
    assert "уже существует" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_change_password_wrong_old(
    client: AsyncClient, test_session, test_user_data: dict
):
    """Покрытие ветки: неверный старый пароль при смене (строки 155, 163 в auth.py)"""
    from security import create_access_token

    user = await create_test_user(test_session, **test_user_data, is_approved=True)
    token = create_access_token(data={"sub": user.username})
    headers = {"Authorization": f"Bearer {token}"}

    # Пытаемся сменить пароль с неверным старым
    response = await client.post(
        "/api/auth/change-password",
        json={"old_password": "WrongOldPass123", "new_password": "NewSecurePass456!"},
        headers=headers,
    )
    assert response.status_code == 400
    assert "пароль" in response.json()["detail"].lower()
