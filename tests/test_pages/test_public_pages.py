import pytest
from fastapi.testclient import TestClient


def test_home_page_renders(sync_client: TestClient):
    # проверка рендеринга главной страницы
    response = sync_client.get("/")
    assert response.status_code == 200
    assert "Ачинск" in response.text
    assert "туристический" in response.text.lower()


def test_attractions_page_renders(sync_client: TestClient):
    # проверка рендеринга страницы достопримечательностей
    response = sync_client.get("/attractions")
    assert response.status_code == 200
    assert (
        "Достопримечательности" in response.text
        or "attractions" in response.text.lower()
    )


def test_accommodations_page_renders(sync_client: TestClient):
    # проверка рендеринга страницы размещений
    response = sync_client.get("/accommodations")
    assert response.status_code == 200
    assert "Гостиницы" in response.text or "accommodations" in response.text.lower()


def test_food_page_renders(sync_client: TestClient):
    # проверка рендеринга страницы заведений питания
    response = sync_client.get("/food")
    assert response.status_code == 200
    assert "Где вкусно" in response.text or "food" in response.text.lower()


def test_events_page_renders(sync_client: TestClient):
    # проверка рендеринга страницы событий
    response = sync_client.get("/events")
    assert response.status_code == 200
    assert "События" in response.text or "events" in response.text.lower()


def test_routes_page_renders(sync_client: TestClient):
    # проверка рендеринга страницы маршрутов
    response = sync_client.get("/routes")
    assert response.status_code == 200
    assert "Маршруты" in response.text or "routes" in response.text.lower()


def test_safety_page_renders(sync_client: TestClient):
    # проверка рендеринга страницы безопасности
    response = sync_client.get("/safety")
    assert response.status_code == 200
    assert "Безопасность" in response.text or "safety" in response.text.lower()


def test_safety_memos_page_renders(sync_client: TestClient):
    # проверка рендеринга страницы памяток безопасности
    response = sync_client.get("/safety_memos")
    assert response.status_code == 200
    assert "Памятки" in response.text or "memos" in response.text.lower()


def test_souvenirs_page_renders(sync_client: TestClient):
    # проверка рендеринга страницы сувениров
    response = sync_client.get("/souvenirs")
    assert response.status_code == 200
    assert "Сувениры" in response.text or "souvenirs" in response.text.lower()


def test_postcards_page_renders(sync_client: TestClient):
    # проверка рендеринга страницы открыток
    response = sync_client.get("/postcards")
    assert response.status_code == 200
    assert "Открытки" in response.text or "postcards" in response.text.lower()


def test_map_page_renders_with_yandex_container(sync_client: TestClient):
    # проверка рендеринга интерактивной карты и наличия контейнера для Яндекс.Карт
    response = sync_client.get("/map")
    assert response.status_code == 200
    assert "map-container" in response.text.lower() or "yandex" in response.text.lower()


def test_contacts_page_renders(sync_client: TestClient):
    # проверка рендеринга страницы контактов
    response = sync_client.get("/contacts")
    assert response.status_code == 200
    assert "Контакты" in response.text or "contacts" in response.text.lower()


def test_inclusive_page_renders(sync_client: TestClient):
    # проверка рендеринга страницы инклюзивного туризма
    response = sync_client.get("/inclusive")
    assert response.status_code == 200
    assert "Инклюзивный" in response.text or "inclusive" in response.text.lower()


def test_public_pages_return_valid_html(sync_client: TestClient):
    # проверка что основные публичные страницы возвращают валидную HTML-структуру
    pages = ["/", "/attractions", "/food", "/events", "/routes", "/map", "/contacts"]
    for page in pages:
        response = sync_client.get(page)
        assert response.status_code == 200
        content = response.text.lower()
        assert "<html" in content or "<!doctype" in content
        assert "</html>" in content


def test_public_404_page_renders(sync_client: TestClient):
    # проверка рендеринга страницы ошибки 404 для несуществующего публичного маршрута
    response = sync_client.get("/nonexistent-public-page-12345")
    assert response.status_code == 404
    assert "не найдена" in response.text.lower() or "404" in response.text
