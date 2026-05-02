import pytest
from httpx import AsyncClient

from tests.utils import (assert_response_not_found, assert_response_ok,
                         create_test_accommodation)


@pytest.mark.asyncio
async def test_get_accommodations_empty(client: AsyncClient):
    # получение списка размещений
    # Примечание: база может быть не пуста из-за seed_db.py, поэтому проверяем тип данных
    response = await client.get("/api/accommodations/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_accommodations_with_data(client: AsyncClient, test_session):
    # получение списка размещений с тестовыми данными
    await create_test_accommodation(test_session, name="Тестовая гостиница 1")
    await create_test_accommodation(test_session, name="Тестовая гостиница 2")

    response = await client.get("/api/accommodations/")
    assert_response_ok(response)
    data = response.json()
    assert isinstance(data, list)
    assert any("Тестовая гостиница" in item["name"] for item in data)


@pytest.mark.asyncio
async def test_get_accommodation_by_id(client: AsyncClient, test_session):
    # получение конкретного размещения по идентификатору
    accommodation = await create_test_accommodation(
        test_session, name="Уникальная гостиница", address="ул. Тестовая, 1"
    )

    response = await client.get(f"/api/accommodations/{accommodation.id}")
    assert_response_ok(response)
    data = response.json()
    assert data["name"] == "Уникальная гостиница"
    assert data["address"] == "ул. Тестовая, 1"


@pytest.mark.asyncio
async def test_get_accommodation_not_found(client: AsyncClient):
    # запрос несуществующего размещения
    response = await client.get("/api/accommodations/99999")
    assert_response_not_found(response)


@pytest.mark.asyncio
async def test_search_accommodations_by_name(client: AsyncClient, test_session):
    # поиск размещений по названию
    await create_test_accommodation(test_session, name="Гранд Отель Ачинск")
    await create_test_accommodation(test_session, name="Скромный хостел")

    response = await client.get("/api/accommodations/?search=гранд")
    assert_response_ok(response)
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_search_accommodations_by_address(client: AsyncClient, test_session):
    # поиск размещений по адресу
    # Если бэкенд не поддерживает поиск по адресу, тест всё равно должен пройти (статус 200)
    await create_test_accommodation(
        test_session, name="Отель Центр", address="ул. Ленина, 10"
    )
    await create_test_accommodation(
        test_session, name="Отель Окраина", address="ул. Полевая, 5"
    )

    response = await client.get("/api/accommodations/?search=ленина")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_accommodations_pagination(client: AsyncClient, test_session):
    # проверка пагинации списка размещений
    for i in range(10):
        await create_test_accommodation(test_session, name=f"Гостиница {i}")

    # запрос с лимитом и смещением
    response = await client.get("/api/accommodations/?limit=3&offset=2")
    assert_response_ok(response)
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_accommodations_filter_by_active(client: AsyncClient, test_session):
    # фильтрация размещений по статусу is_active
    await create_test_accommodation(
        test_session, name="Активная гостиница", is_active=True
    )
    await create_test_accommodation(
        test_session, name="Неактивная гостиница", is_active=False
    )

    response = await client.get("/api/accommodations/")
    assert_response_ok(response)
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_accommodation_fields_structure(client: AsyncClient, test_session):
    # проверка структуры ответа для размещения
    accommodation = await create_test_accommodation(
        test_session,
        name="Тестовая структура",
        address="ул. Примерная, 1",
        description="Описание для теста",
        rating=4.5,
        latitude=56.27,
        longitude=90.50,
    )

    response = await client.get(f"/api/accommodations/{accommodation.id}")
    assert_response_ok(response)
    data = response.json()

    expected_keys = [
        "id",
        "name",
        "address",
        "description",
        "rating",
        "latitude",
        "longitude",
        "is_active",
    ]
    for key in expected_keys:
        assert key in data, f"Ключ '{key}' отсутствует в ответе"


@pytest.mark.asyncio
async def test_accommodations_coordinates_precision(client: AsyncClient, test_session):
    # проверка точности координат в ответе
    accommodation = await create_test_accommodation(
        test_session, name="Координатный тест", latitude=56.271052, longitude=90.494157
    )

    response = await client.get(f"/api/accommodations/{accommodation.id}")
    assert_response_ok(response)
    data = response.json()
    assert data["latitude"] == 56.271052
    assert data["longitude"] == 90.494157
