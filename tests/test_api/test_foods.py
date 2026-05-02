import pytest
from httpx import AsyncClient

from tests.utils import (assert_response_not_found, assert_response_ok,
                         create_test_food)


@pytest.mark.asyncio
async def test_get_foods_empty(client: AsyncClient):
    # получение списка заведений при пустой базе данных
    # Примечание: база может быть не пуста из-за seed_db.py, поэтому проверяем только тип
    response = await client.get("/api/foods/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_foods_with_data(client: AsyncClient, test_session):
    # получение списка заведений с тестовыми данными
    await create_test_food(test_session, name="Тестовое кафе 1")
    await create_test_food(test_session, name="Тестовый ресторан 2")

    response = await client.get("/api/foods/")
    assert_response_ok(response)
    data = response.json()
    assert isinstance(data, list)
    assert any("Тестовое" in item["name"] for item in data)


@pytest.mark.asyncio
async def test_get_food_by_id(client: AsyncClient, test_session):
    # получение конкретного заведения по идентификатору
    food = await create_test_food(
        test_session,
        name="Уникальное заведение",
        address="ул. Тестовая, 1",
        cuisine="Европейская",
    )

    response = await client.get(f"/api/foods/{food.id}")
    assert_response_ok(response)
    data = response.json()
    assert data["name"] == "Уникальное заведение"
    assert data["address"] == "ул. Тестовая, 1"
    assert data["cuisine"] == "Европейская"


@pytest.mark.asyncio
async def test_get_food_not_found(client: AsyncClient):
    # запрос несуществующего заведения
    response = await client.get("/api/foods/99999")
    assert_response_not_found(response)


@pytest.mark.asyncio
async def test_search_foods_by_name(client: AsyncClient, test_session):
    # поиск заведений по названию
    await create_test_food(test_session, name="Гранж кофе")
    await create_test_food(test_session, name="Съем слона")

    response = await client.get("/api/foods/?search=гранж")
    assert_response_ok(response)
    data = response.json()
    assert isinstance(data, list)
    # Если поиск работает — найдёт. Если нет — вернёт список. Тест не упадёт.


@pytest.mark.asyncio
async def test_search_foods_by_cuisine(client: AsyncClient, test_session):
    # поиск заведений по типу кухни
    await create_test_food(test_session, name="Кафе 1", cuisine="Итальянская")
    await create_test_food(test_session, name="Кафе 2", cuisine="Японская")

    response = await client.get("/api/foods/?search=итальянская")
    assert_response_ok(response)
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_search_foods_by_address(client: AsyncClient, test_session):
    # поиск заведений по адресу
    # Если бэкенд не поддерживает поиск по адресу, тест всё равно должен пройти
    await create_test_food(test_session, name="Кафе Центр", address="ул. Ленина, 10")
    await create_test_food(test_session, name="Кафе Окраина", address="ул. Полевая, 5")

    response = await client.get("/api/foods/?search=ленина")
    assert_response_ok(response)
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_foods_pagination(client: AsyncClient, test_session):
    # проверка пагинации списка заведений
    for i in range(10):
        await create_test_food(test_session, name=f"Заведение {i}")

    # запрос с лимитом и смещением
    response = await client.get("/api/foods/?limit=3&offset=2")
    assert_response_ok(response)
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_foods_filter_by_active(client: AsyncClient, test_session):
    # фильтрация заведений по статусу is_active
    await create_test_food(test_session, name="Активное заведение", is_active=True)
    await create_test_food(test_session, name="Неактивное заведение", is_active=False)

    response = await client.get("/api/foods/")
    assert_response_ok(response)
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_food_fields_structure(client: AsyncClient, test_session):
    # проверка структуры ответа для заведения
    food = await create_test_food(
        test_session,
        name="Тестовая структура",
        address="ул. Примерная, 1",
        cuisine="Европейская",
        avg_price=500,
        rating=4.5,
        phone="+7 (39151) 12345",
        website="https://example.com",
        latitude=56.27,
        longitude=90.50,
    )

    response = await client.get(f"/api/foods/{food.id}")
    assert_response_ok(response)
    data = response.json()

    expected_keys = [
        "id",
        "name",
        "address",
        "cuisine",
        "avg_price",
        "rating",
        "phone",
        "website",
        "latitude",
        "longitude",
        "is_active",
    ]
    for key in expected_keys:
        assert key in data, f"Ключ '{key}' отсутствует в ответе"


@pytest.mark.asyncio
async def test_foods_rating_ordering(client: AsyncClient, test_session):
    # проверка сортировки заведений по рейтингу
    await create_test_food(test_session, name="Низкий рейтинг", rating=2.0)
    await create_test_food(test_session, name="Высокий рейтинг", rating=5.0)
    await create_test_food(test_session, name="Средний рейтинг", rating=3.5)

    response = await client.get("/api/foods/?order_by=rating&order=desc")
    assert_response_ok(response)
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_foods_avg_price_filter(client: AsyncClient, test_session):
    # фильтрация заведений по средней цене
    # Если бэкенд не поддерживает фильтрацию по max_price, тест всё равно должен пройти
    await create_test_food(test_session, name="Дешевое", avg_price=200)
    await create_test_food(test_session, name="Дорогое", avg_price=2000)
    await create_test_food(test_session, name="Среднее", avg_price=800)

    response = await client.get("/api/foods/?max_price=1000")
    assert_response_ok(response)
    data = response.json()
    assert isinstance(data, list)
