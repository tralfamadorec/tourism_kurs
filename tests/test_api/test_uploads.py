import io

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_upload_image_success(client: AsyncClient):
    # успешная загрузка валидного изображения
    file_data = {
        "file": ("test_image.jpg", io.BytesIO(b"fake_image_content"), "image/jpeg")
    }
    response = await client.post("/api/upload/", files=file_data)
    assert response.status_code == 200
    data = response.json()
    assert "file_url" in data
    assert "filename" in data
    assert data["filename"].endswith(".jpg")
    assert data["file_url"].startswith("/static/uploads/images/")


@pytest.mark.asyncio
async def test_upload_invalid_extension(client: AsyncClient):
    # загрузка файла с недопустимым расширением
    file_data = {
        "file": ("test_file.txt", io.BytesIO(b"some text content"), "text/plain")
    }
    response = await client.post("/api/upload/", files=file_data)
    assert response.status_code == 400
    assert "Недопустимый формат файла" in response.json()["detail"]


@pytest.mark.asyncio
async def test_upload_invalid_content_type(client: AsyncClient):
    # загрузка файла с валидным расширением, но недопустимым типом контента
    file_data = {
        "file": ("test_image.jpg", io.BytesIO(b"fake_image_content"), "text/plain")
    }
    response = await client.post("/api/upload/", files=file_data)
    assert response.status_code == 400
    assert "Недопустимый формат файла" in response.json()["detail"]


@pytest.mark.asyncio
async def test_upload_file_too_large(client: AsyncClient):
    # попытка загрузить файл размером больше 5 МБ
    large_content = b"x" * (6 * 1024 * 1024)
    file_data = {"file": ("large_image.jpg", io.BytesIO(large_content), "image/jpeg")}
    response = await client.post("/api/upload/", files=file_data)
    assert response.status_code == 400
    assert "Файл слишком большой" in response.json()["detail"]
