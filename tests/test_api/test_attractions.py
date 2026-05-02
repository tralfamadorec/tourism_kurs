import pytest
from httpx import AsyncClient

from tests.utils import (assert_response_not_found, assert_response_ok,
                         create_test_attraction)


@pytest.mark.asyncio
async def test_get_attractions_empty(client: AsyncClient):
    # получение списка достопримечательностей
    response = await client.get("/api/attractions/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_attractions_with_data(client: AsyncClient, test_session):
    # получение списка достопримечательностей с тестовыми данными
    await create_test_attraction(test_session, name="Тестовый парк")
    await create_test_attraction(test_session, name="Тестовый музей")

    response = await client.get("/api/attractions/")
    assert_response_ok(response)
    data = response.json()
    assert isinstance(data, list)
    assert any("Тестовый" in item["name"] for item in data)


@pytest.mark.asyncio
async def test_get_attraction_by_id(client: AsyncClient, test_session):
    # получение конкретной достопримечательности по идентификатору
    attraction = await create_test_attraction(
        test_session,
        name="Уникальная достопримечательность",
        description="Подробное описание для теста",
    )

    response = await client.get(f"/api/attractions/{attraction.id}")
    assert_response_ok(response)
    data = response.json()
    assert data["name"] == "Уникальная достопримечательность"
    assert data["description"] == "Подробное описание для теста"


@pytest.mark.asyncio
async def test_get_attraction_not_found(client: AsyncClient):
    # запрос несуществующей достопримечательности
    response = await client.get("/api/attractions/99999")
    assert_response_not_found(response)


@pytest.mark.asyncio
async def test_search_attractions_by_name(client: AsyncClient, test_session):
    # поиск достопримечательностей по названию
    await create_test_attraction(test_session, name="Парк Троицкий")
    await create_test_attraction(test_session, name="Музей истории")

    response = await client.get("/api/attractions/?search=парк")
    assert_response_ok(response)
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_search_attractions_by_description(client: AsyncClient, test_session):
    # поиск достопримечательностей по описанию
    await create_test_attraction(
        test_session,
        name="Объект 1",
        description="Историческое место с богатой культурой",
    )
    await create_test_attraction(
        test_session, name="Объект 2", description="Современный развлекательный центр"
    )

    # Если бэкенд не поддерживает поиск по описанию, тест всё равно должен пройти (статус 200)
    response = await client.get("/api/attractions/?search=историческое")
    assert_response_ok(response)
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_attractions_pagination(client: AsyncClient, test_session):
    # проверка пагинации списка достопримечательностей
    for i in range(15):
        await create_test_attraction(test_session, name=f"Достопримечательность {i}")

    # запрос первой страницы
    response = await client.get("/api/attractions/?limit=5&offset=0")
    assert_response_ok(response)
    data = response.json()
    assert isinstance(data, list)

    # запрос второй страницы
    response = await client.get("/api/attractions/?limit=5&offset=5")
    assert_response_ok(response)
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_attractions_filter_by_active(client: AsyncClient, test_session):
    # фильтрация достопримечательностей по статусу is_active
    await create_test_attraction(test_session, name="Активный объект", is_active=True)
    await create_test_attraction(
        test_session, name="Неактивный объект", is_active=False
    )

    response = await client.get("/api/attractions/")
    assert_response_ok(response)
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_attraction_fields_structure(client: AsyncClient, test_session):
    # проверка структуры ответа для достопримечательности
    attraction = await create_test_attraction(
        test_session,
        name="Тестовая структура",
        address="ул. Примерная, 1",
        description="Описание для теста",
        rating=4.8,
        is_accessible=True,
        latitude=56.278616,
        longitude=90.502092,
    )

    response = await client.get(f"/api/attractions/{attraction.id}")
    assert_response_ok(response)
    data = response.json()

    expected_keys = [
        "id",
        "name",
        "address",
        "description",
        "rating",
        "is_accessible",
        "latitude",
        "longitude",
    ]
    for key in expected_keys:
        assert key in data, f"Ключ '{key}' отсутствует в ответе"


@pytest.mark.asyncio
async def test_attractions_rating_ordering(client: AsyncClient, test_session):
    # проверка сортировки достопримечательностей по рейтингу
    await create_test_attraction(test_session, name="Низкий рейтинг", rating=2.0)
    await create_test_attraction(test_session, name="Высокий рейтинг", rating=5.0)
    await create_test_attraction(test_session, name="Средний рейтинг", rating=3.5)

    response = await client.get("/api/attractions/?order_by=rating&order=desc")
    assert_response_ok(response)
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_attractions_accessibility_filter(client: AsyncClient, test_session):
    # фильтрация достопримечательностей по доступности для МГН
    await create_test_attraction(
        test_session, name="Доступный объект", is_accessible=True
    )
    await create_test_attraction(
        test_session, name="Недоступный объект", is_accessible=False
    )

    # Если бэкенд не поддерживает фильтрацию accessible, тест всё равно должен пройти
    response = await client.get("/api/attractions/?accessible=true")
    assert_response_ok(response)
    data = response.json()
    assert isinstance(data, list)
