from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from pydantic import BaseModel, Field

from database import get_db
from models import PostcardTemplate, User
from schemas import PostcardTemplateResponse
from security import get_current_user

router = APIRouter(prefix="/api/postcards", tags=["Открытки"])

@router.get("/", response_model=List[PostcardTemplateResponse])
async def get_templates(db: AsyncSession = Depends(get_db)):
    """Получение списка активных шаблонов открыток (публичный)"""
    result = await db.execute(
        select(PostcardTemplate).where(PostcardTemplate.is_active == True)
    )
    return result.scalars().all()

class PostcardGenerateRequest(BaseModel):
    template_id: int = Field(..., ge=1, description="ID выбранного шаблона")
    message: str = Field(..., min_length=1, max_length=500, description="Текст поздравления")
    recipient: Optional[str] = Field(None, max_length=100, description="Имя получателя")

@router.post("/generate")
async def generate_postcard(
    gen_data: PostcardGenerateRequest,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(PostcardTemplate).where(PostcardTemplate.id == gen_data.template_id)
    )
    template = result.scalar_one_or_none()
    
    if not template or not template.is_active:
        raise HTTPException(status_code=404, detail="Шаблон не найден или недоступен")

    return {
        "status": "success",
        "message": "Открытка успешно сгенерирована",
        "template_url": template.image_url,
        "text": gen_data.message,
        "recipient": gen_data.recipient,
        "download_url": f"{template.image_url}?generated=true"
    }

class PostcardTemplateCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    image_url: str
    description: Optional[str] = None

class PostcardTemplateUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=2, max_length=255)
    image_url: Optional[str] = None
    description: Optional[str] = None

@router.post("/", response_model=PostcardTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    template_data: PostcardTemplateCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_obj = PostcardTemplate(**template_data.model_dump())
    db.add(new_obj)
    await db.commit()
    await db.refresh(new_obj)
    return new_obj

@router.get("/{template_id}", response_model=PostcardTemplateResponse)
async def get_template(
    template_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(PostcardTemplate).where(PostcardTemplate.id == template_id)
    )
    obj = result.scalar_one_or_none()
    
    if not obj:
        raise HTTPException(status_code=404, detail="Шаблон не найден")
        
    return obj

@router.put("/{template_id}", response_model=PostcardTemplateResponse)
async def update_template(
    template_id: int,
    template_data: PostcardTemplateUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(PostcardTemplate).where(PostcardTemplate.id == template_id)
    )
    obj = result.scalar_one_or_none()
    
    if not obj:
        raise HTTPException(status_code=404, detail="Шаблон не найден")
    
    for key, value in template_data.model_dump(exclude_unset=True).items():
        setattr(obj, key, value)
    
    await db.commit()
    await db.refresh(obj)
    return obj

@router.delete("/{template_id}")
async def delete_template(
    template_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(PostcardTemplate).where(PostcardTemplate.id == template_id)
    )
    obj = result.scalar_one_or_none()
    
    if not obj:
        raise HTTPException(status_code=404, detail="Шаблон не найден")
        
    obj.is_active = False
    await db.commit()
    
    return {"message": "Шаблон успешно удалён"}