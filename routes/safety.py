from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from database import get_db
from models import SafetyObject
from schemas import SafetyObjectCreate, SafetyObjectResponse, SafetyObjectUpdate
from security import get_current_user
from models import User

router = APIRouter(prefix="/api/safety", tags=["Безопасность"])

@router.get("/", response_model=List[SafetyObjectResponse])
async def get_safety_objects(
    limit: int = Query(50, ge=1, le=100),
    skip: int = Query(0, ge=0),
    category: Optional[str] = Query(None, description="Категория (Полиция, МЧС...)"),
    search: Optional[str] = Query(None, description="Поиск по названию"),
    db: AsyncSession = Depends(get_db)
):
    query = select(SafetyObject).where(SafetyObject.is_active == True)
    
    if category:
        query = query.where(SafetyObject.category.ilike(f"%{category}%"))
    if search:
        query = query.where(SafetyObject.name.ilike(f"%{search}%"))
        
    query = query.order_by(SafetyObject.category.asc(), SafetyObject.name.asc())
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
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

@router.post("/", response_model=SafetyObjectResponse, status_code=status.HTTP_201_CREATED)
async def create_safety_object(
    obj_data: SafetyObjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_obj = SafetyObject(**obj_data.model_dump(), created_by=current_user.id)
    db.add(new_obj)
    await db.commit()
    await db.refresh(new_obj)
    return new_obj

@router.put("/{safety_id}", response_model=SafetyObjectResponse)
async def update_safety_object(
    safety_id: int,
    obj_data: SafetyObjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(SafetyObject).where(SafetyObject.id == safety_id))
    obj = result.scalar_one_or_none()
    
    if not obj:
        raise HTTPException(status_code=404, detail="Объект не найден")
    
    for key, value in obj_data.model_dump(exclude_unset=True).items():
        setattr(obj, key, value)
        
    await db.commit()
    await db.refresh(obj)
    return obj

@router.delete("/{safety_id}")
async def delete_safety_object(
    safety_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(SafetyObject).where(SafetyObject.id == safety_id))
    obj = result.scalar_one_or_none()
    
    if not obj:
        raise HTTPException(status_code=404, detail="Объект не найден")
    
    obj.is_active = False
    await db.commit()
    
    return {"message": "Запись удалена"}