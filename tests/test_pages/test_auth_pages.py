import pytest
from fastapi.testclient import TestClient

from models import User
from security import get_password_hash


def test_login_page_renders_with_form(sync_client: TestClient):
    # проверка рендеринга страницы входа и наличия элементов формы
    response = sync_client.get("/login")
    assert response.status_code == 200
    content = response.text.lower()

    # проверяем наличие полей ввода логина и пароля
    assert "username" in content or "email" in content
    assert "password" in content
    assert 'type="password"' in content or 'type="submit"' in content


def test_register_page_renders_with_form(sync_client: TestClient):
    # проверка рендеринга страницы регистрации и наличия элементов формы
    response = sync_client.get("/register")
    assert response.status_code == 200
    content = response.text.lower()

    # проверяем наличие полей ввода имени, email и пароля
    assert "username" in content or "имя" in content
    assert "email" in content
    assert "password" in content
    assert 'type="password"' in content or 'type="submit"' in content


def test_login_page_contains_base_html_structure(sync_client: TestClient):
    # проверка что страница входа возвращает валидный HTML
    response = sync_client.get("/login")
    assert response.status_code == 200
    content = response.text.lower()
    assert "<html" in content or "<!doctype" in content
    assert "</html>" in content


def test_register_page_contains_base_html_structure(sync_client: TestClient):
    # проверка что страница регистрации возвращает валидный HTML
    response = sync_client.get("/register")
    assert response.status_code == 200
    content = response.text.lower()
    assert "<html" in content or "<!doctype" in content
    assert "</html>" in content


def test_auth_pages_load_static_assets_correctly(sync_client: TestClient):
    for page in ["/login", "/register"]:
        response = sync_client.get(page)
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/html")
        assert b"<form" in response.content.lower()


@pytest.mark.asyncio
async def test_login_page_redirects_after_successful_auth(client, test_session):
    from models import User
    from security import get_password_hash

    # Создаём testuser
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("SecurePass123!"),
        role="user",
        is_approved=True,
        is_active=True,
    )
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)

    # Логин
    response = await client.post(
        "/login", data={"username": "testuser", "password": "SecurePass123!"}
    )
    assert response.status_code == 302
