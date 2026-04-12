from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from pydantic import BaseModel, Field
from typing import Optional

from database import get_db
from models import PostcardTemplate
from schemas import PostcardTemplateResponse

router = APIRouter(prefix="/api/postcards", tags=["Открытки"])

class PostcardGenerateRequest(BaseModel):
    template_id: int = Field(..., ge=1, description="ID выбранного шаблона")
    message: str = Field(..., min_length=1, max_length=500, description="Текст поздравления")
    recipient: Optional[str] = Field(None, max_length=100, description="Имя получателя")

@router.get("/", response_model=List[PostcardTemplateResponse])
async def get_templates(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PostcardTemplate).where(PostcardTemplate.is_active == True))
    return result.scalars().all()

@router.post("/generate")
async def generate_postcard(data: PostcardGenerateRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PostcardTemplate).where(PostcardTemplate.id == data.template_id))
    template = result.scalar_one_or_none()
    
    if not template:
        raise HTTPException(status_code=404, detail="Шаблон открытки не найден")
        
    if not template.is_active:
        raise HTTPException(status_code=400, detail="Данный шаблон временно недоступен")

    # в продакшене здесь будет вызов PIL/cairo для наложения текста на изображение
    # для текущего MVP возвращает структуру ответа, готовую к интеграции с фронтендом
    return {
        "status": "success",
        "message": "Открытка успешно сгенерирована",
        "template_url": template.image_url,
        "text": data.message,
        "recipient": data.recipient,
        "download_url": f"{template.image_url}?generated=true" # заглушка для скачивания
    }