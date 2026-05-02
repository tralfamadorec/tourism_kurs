import pytest
from fastapi.testclient import TestClient


def test_admin_dashboard_redirects_unauthorized(sync_client: TestClient):
    # проверка редиректа с главной страницы админки при отсутствии авторизации
    response = sync_client.get("/admin", follow_redirects=False)
    assert response.status_code == 302
    assert "/login?next=/admin" in response.headers.get("location", "")


def test_admin_attractions_pages_redirect_unauthorized(sync_client: TestClient):
    # проверка защиты разделов достопримечательностей в админке
    routes = [
        "/admin/attractions",
        "/admin/attractions/new",
        "/admin/attractions/1/edit",
    ]
    for route in routes:
        response = sync_client.get(route, follow_redirects=False)
        assert (
            response.status_code == 302
        ), f"Раздел {route} должен требовать авторизации"


def test_admin_routes_pages_redirect_unauthorized(sync_client: TestClient):
    # проверка защиты разделов маршрутов в админке
    routes = ["/admin/routes", "/admin/routes/new", "/admin/routes/1/edit"]
    for route in routes:
        response = sync_client.get(route, follow_redirects=False)
        assert (
            response.status_code == 302
        ), f"Раздел {route} должен требовать авторизации"


def test_admin_hotels_pages_redirect_unauthorized(sync_client: TestClient):
    # проверка защиты разделов гостиниц в админке
    routes = ["/admin/hotels", "/admin/hotels/new", "/admin/hotels/1/edit"]
    for route in routes:
        response = sync_client.get(route, follow_redirects=False)
        assert (
            response.status_code == 302
        ), f"Раздел {route} должен требовать авторизации"


def test_admin_foods_pages_redirect_unauthorized(sync_client: TestClient):
    # проверка защиты разделов заведений в админке
    routes = ["/admin/foods", "/admin/foods/new", "/admin/foods/1/edit"]
    for route in routes:
        response = sync_client.get(route, follow_redirects=False)
        assert (
            response.status_code == 302
        ), f"Раздел {route} должен требовать авторизации"


def test_admin_events_pages_redirect_unauthorized(sync_client: TestClient):
    # проверка защиты разделов событий в админке
    routes = ["/admin/events", "/admin/events/new", "/admin/events/1/edit"]
    for route in routes:
        response = sync_client.get(route, follow_redirects=False)
        assert (
            response.status_code == 302
        ), f"Раздел {route} должен требовать авторизации"


def test_admin_souvenirs_pages_redirect_unauthorized(sync_client: TestClient):
    # проверка защиты разделов сувениров в админке
    routes = ["/admin/souvenirs", "/admin/souvenirs/new", "/admin/souvenirs/1/edit"]
    for route in routes:
        response = sync_client.get(route, follow_redirects=False)
        assert (
            response.status_code == 302
        ), f"Раздел {route} должен требовать авторизации"


def test_admin_safety_pages_redirect_unauthorized(sync_client: TestClient):
    # проверка защиты разделов безопасности в админке
    routes = ["/admin/safety", "/admin/safety/new", "/admin/safety/1/edit"]
    for route in routes:
        response = sync_client.get(route, follow_redirects=False)
        assert (
            response.status_code == 302
        ), f"Раздел {route} должен требовать авторизации"


def test_admin_memos_pages_redirect_unauthorized(sync_client: TestClient):
    # проверка защиты разделов памяток в админке
    routes = ["/admin/memos", "/admin/memos/new", "/admin/memos/1/edit"]
    for route in routes:
        response = sync_client.get(route, follow_redirects=False)
        assert (
            response.status_code == 302
        ), f"Раздел {route} должен требовать авторизации"


def test_admin_postcards_pages_redirect_unauthorized(sync_client: TestClient):
    # проверка защиты разделов открыток в админке
    routes = ["/admin/postcards", "/admin/postcards/new", "/admin/postcards/1/edit"]
    for route in routes:
        response = sync_client.get(route, follow_redirects=False)
        assert (
            response.status_code == 302
        ), f"Раздел {route} должен требовать авторизации"


def test_admin_users_and_profile_redirect_unauthorized(sync_client: TestClient):
    # проверка защиты списка пользователей и профиля администратора
    routes = ["/admin/users", "/admin/profile", "/admin/themes"]
    for route in routes:
        response = sync_client.get(route, follow_redirects=False)
        assert (
            response.status_code == 302
        ), f"Раздел {route} должен требовать авторизации"


def test_admin_redirect_preserves_next_parameter(sync_client: TestClient):
    # проверка что редирект сохраняет исходный URL в параметре next
    response = sync_client.get("/admin/attractions/new", follow_redirects=False)
    location = response.headers.get("location", "")
    assert "/login" in location
    assert "next=" in location
    assert "/admin/attractions/new" in location
