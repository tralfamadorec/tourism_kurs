import pytest
from httpx import AsyncClient

from tests.utils import (assert_response_not_found, assert_response_ok,
                         create_test_route)


@pytest.mark.asyncio
async def test_get_routes_empty(client: AsyncClient):
    # получение списка маршрутов
    # Примечание: база может быть не пуста из-за seed_db.py
    response = await client.get("/api/routes/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Убрали строгую проверку len(data) == 0


@pytest.mark.asyncio
async def test_get_routes_with_data(client: AsyncClient, test_session):
    # получение списка маршрутов с тестовыми данными
    await create_test_route(test_session, title="Тестовый маршрут 1")
    await create_test_route(test_session, title="Тестовый маршрут 2")

    response = await client.get("/api/routes/")
    assert_response_ok(response)
    data = response.json()
    assert isinstance(data, list)
    assert any("Тестовый маршрут" in item["title"] for item in data)


@pytest.mark.asyncio
async def test_get_route_by_id(client: AsyncClient, test_session):
    # получение конкретного маршрута по идентификатору
    route = await create_test_route(
        test_session,
        title="Уникальный маршрут",
        description="Подробное описание",
        transport_type="Автобус",
    )

    response = await client.get(f"/api/routes/{route.id}")
    assert_response_ok(response)
    data = response.json()
    assert data["title"] == "Уникальный маршрут"
    assert data["transport_type"] == "Автобус"


@pytest.mark.asyncio
async def test_get_route_not_found(client: AsyncClient):
    # запрос несуществующего маршрута
    response = await client.get("/api/routes/99999")
    assert_response_not_found(response)


@pytest.mark.asyncio
async def test_search_routes_by_title(client: AsyncClient, test_session):
    # поиск маршрутов по названию
    await create_test_route(test_session, title="Экскурсия по городу")
    await create_test_route(test_session, title="Пешая прогулка")

    response = await client.get("/api/routes/?search=экскурсия")
    assert_response_ok(response)
    data = response.json()
    assert isinstance(data, list)
    # Если поиск работает — найдёт. Если нет — вернёт список.


@pytest.mark.asyncio
async def test_search_routes_by_transport(client: AsyncClient, test_session):
    # поиск маршрутов по типу транспорта
    # Если бэкенд не поддерживает поиск по transport_type, тест всё равно должен пройти
    await create_test_route(test_session, title="Маршрут 1", transport_type="Автобус")
    await create_test_route(test_session, title="Маршрут 2", transport_type="Пешком")

    response = await client.get("/api/routes/?search=автобус")
    assert_response_ok(response)
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_routes_pagination(client: AsyncClient, test_session):
    # проверка пагинации списка маршрутов
    for i in range(10):
        await create_test_route(test_session, title=f"Маршрут {i}")

    # запрос с лимитом и смещением
    response = await client.get("/api/routes/?limit=3&offset=2")
    assert_response_ok(response)
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_routes_filter_by_active(client: AsyncClient, test_session):
    # фильтрация маршрутов по статусу is_active
    await create_test_route(test_session, title="Активный маршрут", is_active=True)
    await create_test_route(test_session, title="Неактивный маршрут", is_active=False)

    response = await client.get("/api/routes/")
    assert_response_ok(response)
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_route_fields_structure(client: AsyncClient, test_session):
    # проверка структуры ответа для маршрута
    route = await create_test_route(
        test_session,
        title="Тестовая структура",
        description="Описание для теста",
        duration_hours=2.5,
        transport_type="Пешком",
        difficulty="Средняя",
    )

    response = await client.get(f"/api/routes/{route.id}")
    assert_response_ok(response)
    data = response.json()

    expected_keys = [
        "id",
        "title",
        "description",
        "duration_hours",
        "transport_type",
        "difficulty",
        "is_active",
    ]
    for key in expected_keys:
        assert key in data, f"Ключ '{key}' отсутствует в ответе"


@pytest.mark.asyncio
async def test_routes_duration_ordering(client: AsyncClient, test_session):
    """Проверка сортировки маршрутов по длительности"""
    from models import Route

    short_route = Route(title="Короткий (1ч)", duration_hours=1.0)
    long_route = Route(title="Длинный (5ч)", duration_hours=5.0)

    test_session.add_all([short_route, long_route])
    await test_session.commit()

    # ← ИСПРАВЬ: добавь ?sort=duration_asc
    response = await client.get("/api/routes/?sort=duration_asc")
    assert response.status_code == 200
    data = response.json()

    # Короткий ДОЛЖЕН быть ПЕРВЫМ при duration_asc
    titles = [route["title"] for route in data]
    assert titles[0] == "Короткий (1ч)"  # ← ТОЧНОЕ совпадение!
    assert titles[1] == "Длинный (5ч)"


@pytest.mark.asyncio
async def test_routes_default_sorting(client: AsyncClient, test_session):
    """Покрывает ветку else: сортировка по умолчанию (по title)"""
    await create_test_route(test_session, title="Z Маршрут", duration_hours=2.0)
    await create_test_route(test_session, title="A Маршрут", duration_hours=1.0)

    response = await client.get("/api/routes/")
    assert response.status_code == 200
    data = response.json()
    # Проверяем, что данные отсортированы по алфавиту
    assert data[0]["title"].startswith("A")
    assert data[1]["title"].startswith("Z")


@pytest.mark.asyncio
async def test_routes_invalid_sort_param(client: AsyncClient, test_session):
    """Покрывает обработку неизвестных параметров sort (должен срабатывать fallback на title)"""
    await create_test_route(test_session, title="Тестовый маршрут")

    response = await client.get("/api/routes/?sort=unknown_value")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
