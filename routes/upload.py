import logging
import shutil
import uuid
import imghdr
from pathlib import Path
from fastapi import APIRouter, File, HTTPException, UploadFile
from PIL import Image
import io

logger = logging.getLogger(__name__)

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "static" / "uploads" / "images"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
ALLOWED_MIME = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_SIZE = 5 * 1024 * 1024  # 5MB


@router.post("/api/upload/")
async def upload_file(file: UploadFile = File(...)):
    logger.info("Загрузка файла: %s", file.filename)
    
    file_ext = Path(file.filename or "").suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        logger.warning("Недопустимое расширение файла: %s", file.filename)
        raise HTTPException(status_code=400, detail="Недопустимый формат файла")

    if file.content_type not in ALLOWED_MIME:
        logger.warning("Недопустимый MIME-тип: %s", file.content_type)
        raise HTTPException(status_code=400, detail="Недопустимый тип содержимого")

    content = await file.read()
    if len(content) > MAX_SIZE:
        logger.warning("Файл превышает лимит размера: %s (%d байт)", file.filename, len(content))
        raise HTTPException(status_code=400, detail="Файл слишком большой (макс. 5MB)")

    try:
        img = Image.open(io.BytesIO(content))
        img.verify()
        img = Image.open(io.BytesIO(content))
        if img.format.lower() not in {"jpeg", "png", "webp", "gif"}:
            raise ValueError("Неподдерживаемый формат")
    except Exception as e:
        logger.warning("Ошибка валидации изображения: %s", e)
        raise HTTPException(status_code=400, detail="Файл не является корректным изображением")

    unique_filename = f"{uuid.uuid4().hex}{file_ext}"
    file_path = UPLOAD_DIR / unique_filename

    with open(file_path, "wb") as buffer:
        buffer.write(content)

    logger.info("Файл успешно загружен: %s", unique_filename)
    file_url = f"/static/uploads/images/{unique_filename}"
    return {"file_url": file_url, "filename": unique_filename}