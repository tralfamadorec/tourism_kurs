from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from database import get_db
from models import SafetyObject
from schemas import SafetyObjectResponse

router = APIRouter(prefix="/api/safety", tags=["Безопасность"])

@router.get("/", response_model=List[SafetyObjectResponse])
async def get_safety_objects(
    category: Optional[str] = Query(None, description="Фильтр по категории (Полиция, МЧС, Медицина)"),
    search: Optional[str] = Query(None, description="Нечеткий поиск по названию"),
    db: AsyncSession = Depends(get_db)
):
    query = select(SafetyObject).where(SafetyObject.is_active == True)
    
    if category:
        query = query.where(SafetyObject.category.ilike(f"%{category}%"))
        
    if search:
        query = query.where(SafetyObject.name.ilike(f"%{search}%"))
        
    result = await db.execute(query.order_by(SafetyObject.category, SafetyObject.name))
    return result.scalars().all()

@router.get("/{safety_id}", response_model=SafetyObjectResponse)
async def get_safety_object_by_id(safety_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(SafetyObject)
        .where(SafetyObject.id == safety_id)
        .where(SafetyObject.is_active == True)
    )
    obj = result.scalar_one_or_none()
    
    if not obj:
        raise HTTPException(status_code=404, detail="Объект безопасности не найден")
        
    return obj

# POST/PUT/DELETE не реализованы, так как в ТЗ раздел «Безопасность»
# указан как публичный справочник (только GET). При необходимости администрирования
# эти методы можно добавить позже по аналогии с другими роутерами