import pytest
from httpx import AsyncClient

from models import SafetyMemo
from tests.utils import assert_response_not_found, assert_response_ok

# Эндпоинт /api/safety/memos/ пока не зарегистрирован в приложении


# Вспомогательная функция для создания памятки
async def create_test_safety_memo(
    session, title="Тестовая памятка", content="Текст", order=1
):
    memo = SafetyMemo(title=title, content=content, order=order)
    session.add(memo)
    await session.commit()
    await session.refresh(memo)
    return memo


@pytest.mark.asyncio
async def test_get_safety_memos_empty(client: AsyncClient):
    # получение списка памяток при пустой базе данных
    response = await client.get("/api/safety/memos/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_safety_memos_with_data(client: AsyncClient, test_session):
    # получение списка памяток с тестовыми данными
    await create_test_safety_memo(test_session, title="Правила 1", order=1)
    await create_test_safety_memo(test_session, title="Правила 2", order=2)

    response = await client.get("/api/safety/memos/")
    assert_response_ok(response)
    data = response.json()
    assert len(data) >= 2
    assert data[0]["order"] <= data[1]["order"]


@pytest.mark.asyncio
async def test_get_safety_memo_by_id(client: AsyncClient, test_session):
    # получение конкретной памятки по идентификатору
    memo = await create_test_safety_memo(
        test_session, title="Уникальная памятка", content="Важный текст", order=5
    )

    response = await client.get(f"/api/safety/memos/{memo.id}")
    assert_response_ok(response)
    data = response.json()
    assert data["title"] == "Уникальная памятка"
    assert data["content"] == "Важный текст"
    assert data["order"] == 5


@pytest.mark.asyncio
async def test_get_safety_memo_not_found(client: AsyncClient):
    # запрос несуществующей памятки
    response = await client.get("/api/safety/memos/99999")
    assert_response_not_found(response)


@pytest.mark.asyncio
async def test_safety_memos_pagination(client: AsyncClient, test_session):
    # проверка пагинации списка памяток
    for i in range(10):
        await create_test_safety_memo(test_session, title=f"Памятка {i}", order=i)

    # запрос с лимитом и смещением
    response = await client.get("/api/safety/memos/?limit=3&offset=2")
    assert_response_ok(response)
    data = response.json()
    assert len(data) == 3


@pytest.mark.asyncio
async def test_safety_memo_fields_structure(client: AsyncClient, test_session):
    # проверка структуры ответа для памятки
    memo = await create_test_safety_memo(
        test_session,
        title="Тестовая структура",
        content="Текст для проверки полей",
        order=10,
    )

    response = await client.get(f"/api/safety/memos/{memo.id}")
    assert_response_ok(response)
    data = response.json()

    expected_keys = ["id", "title", "content", "order"]
    for key in expected_keys:
        assert key in data, f"Ключ '{key}' отсутствует в ответе"
