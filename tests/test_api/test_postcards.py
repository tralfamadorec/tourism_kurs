import pytest
from httpx import AsyncClient

from tests.utils import (assert_response_not_found, assert_response_ok,
                         create_test_postcard)


@pytest.mark.asyncio
async def test_get_postcards_empty(client: AsyncClient):
    # получение списка шаблонов открыток при пустой базе данных
    response = await client.get("/api/postcards/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_postcards_with_data(client: AsyncClient, test_session):
    # получение списка шаблонов открыток с тестовыми данными
    # ИСПРАВЛЕНО: name -> title (соответствует модели PostcardTemplate)
    await create_test_postcard(test_session, title="Тестовая открытка 1")
    await create_test_postcard(test_session, title="Тестовая открытка 2")

    response = await client.get("/api/postcards/")
    assert_response_ok(response)
    data = response.json()
    assert isinstance(data, list)
    assert any("Тестовая открытка" in item["title"] for item in data)


@pytest.mark.asyncio
async def test_get_postcard_by_id(client: AsyncClient, test_session):
    # получение конкретного шаблона открытки по идентификатору
    postcard = await create_test_postcard(
        test_session,
        title="Уникальная открытка",  # ИСПРАВЛЕНО: name -> title
        description="Описание для теста",
        image_url="/static/images/test.jpg",
    )

    response = await client.get(f"/api/postcards/{postcard.id}")
    assert_response_ok(response)
    data = response.json()
    assert data["title"] == "Уникальная открытка"  # ИСПРАВЛЕНО: name -> title
    assert data["description"] == "Описание для теста"
    assert data["image_url"] == "/static/images/test.jpg"


@pytest.mark.asyncio
async def test_get_postcard_not_found(client: AsyncClient):
    # запрос несуществующего шаблона открытки
    response = await client.get("/api/postcards/99999")
    assert_response_not_found(response)


@pytest.mark.asyncio
async def test_search_postcards_by_name(client: AsyncClient, test_session):
    # поиск шаблонов открыток по названию
    await create_test_postcard(test_session, title="Администрация")  # ИСПРАВЛЕНО
    await create_test_postcard(test_session, title="Георгий Победоносец")  # ИСПРАВЛЕНО

    response = await client.get("/api/postcards/?search=администрация")
    assert_response_ok(response)
    data = response.json()
    assert isinstance(data, list)
    assert any("Администрация" in item["title"] for item in data)


@pytest.mark.asyncio
async def test_search_postcards_by_description(client: AsyncClient, test_session):
    # поиск шаблонов открыток по описанию
    await create_test_postcard(
        test_session,
        title="Открытка 1",  # ИСПРАВЛЕНО
        description="Здание администрации города",
    )
    await create_test_postcard(
        test_session,
        title="Открытка 2",  # ИСПРАВЛЕНО
        description="Скульптура Георгия Победоносца",
    )

    response = await client.get("/api/postcards/?search=здание")
    assert_response_ok(response)
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_postcards_pagination(client: AsyncClient, test_session):
    # проверка пагинации списка шаблонов открыток
    for i in range(8):
        await create_test_postcard(test_session, title=f"Открытка {i}")  # ИСПРАВЛЕНО

    # запрос первой страницы
    response = await client.get("/api/postcards/?limit=3&offset=0")
    assert_response_ok(response)
    data = response.json()
    assert isinstance(data, list)

    # запрос второй страницы
    response = await client.get("/api/postcards/?limit=3&offset=3")
    assert_response_ok(response)
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_postcard_fields_structure(client: AsyncClient, test_session):
    # проверка структуры ответа для шаблона открытки
    postcard = await create_test_postcard(
        test_session,
        title="Тестовая структура",  # ИСПРАВЛЕНО
        description="Описание для теста",
        image_url="/static/images/test_image.jpg",
    )

    response = await client.get(f"/api/postcards/{postcard.id}")
    assert_response_ok(response)
    data = response.json()

    # ИСПРАВЛЕНО: в ответе поле title, а не name
    expected_keys = ["id", "title", "description", "image_url"]
    for key in expected_keys:
        assert key in data, f"Ключ '{key}' отсутствует в ответе"


@pytest.mark.asyncio
async def test_postcard_image_url_format(client: AsyncClient, test_session):
    # проверка формата URL изображения
    postcard = await create_test_postcard(
        test_session,
        title="Открытка с изображением",  # ИСПРАВЛЕНО
        image_url="/static/images/administracia.jpg",
    )

    response = await client.get(f"/api/postcards/{postcard.id}")
    assert_response_ok(response)
    data = response.json()

    assert data["image_url"].startswith("/static/images/")
    assert data["image_url"].endswith(".jpg")


@pytest.mark.asyncio
async def test_postcards_with_real_data(client: AsyncClient, test_session):
    # проверка с реальными данными из документации
    await create_test_postcard(
        test_session,
        title="Администрация",  # ИСПРАВЛЕНО
        description="Здание администрации города",
        image_url="/static/images/administracia.jpg",
    )
    await create_test_postcard(
        test_session,
        title="Георгий Победоносец",  # ИСПРАВЛЕНО
        description="Скульптура Георгия Победоносца в историко-культурном парке",
        image_url="/static/images/pobedonosec.jpg",
    )
    await create_test_postcard(
        test_session,
        title="Стела",  # ИСПРАВЛЕНО
        description="Памятная стела",
        image_url="/static/images/stela.jpg",
    )

    response = await client.get("/api/postcards/")
    assert_response_ok(response)
    data = response.json()
    assert isinstance(data, list)

    # проверяем наличие конкретных открыток
    titles = [item["title"] for item in data]  # ИСПРАВЛЕНО: name -> title
    assert "Администрация" in titles
    assert "Георгий Победоносец" in titles
    assert "Стела" in titles
