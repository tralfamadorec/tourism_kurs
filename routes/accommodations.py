from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from database import get_db
from models import Accommodation
from schemas import AccommodationCreate, AccommodationUpdate, AccommodationResponse
from security import get_current_user
from models import User

router = APIRouter(prefix="/api/accommodations", tags=["Гостиницы"])

@router.get("/", response_model=List[AccommodationResponse])
async def get_accommodations(
    limit: int = Query(50, ge=1, le=100),
    skip: int = Query(0, ge=0),
    search: Optional[str] = Query(None, description="Поиск по названию"),
    max_price: Optional[int] = Query(None, ge=0),
    min_rating: Optional[float] = Query(None, ge=0, le=5),
    sort: str = Query("rating", description="rating, price_asc, price_desc, name"),
    db: AsyncSession = Depends(get_db)
):
    """Получение списка гостиниц с фильтрами"""
    query = select(Accommodation).where(Accommodation.is_active == True)
    
    # поиск
    if search:
        query = query.where(Accommodation.name.ilike(f"%{search}%"))
    
    # фильтры
    if max_price:
        query = query.where(Accommodation.price_per_night <= max_price)
    if min_rating:
        query = query.where(Accommodation.rating >= min_rating)
    
    # сортировка
    if sort == "price_asc":
        query = query.order_by(Accommodation.price_per_night.asc())
    elif sort == "price_desc":
        query = query.order_by(Accommodation.price_per_night.desc())
    elif sort == "name":
        query = query.order_by(Accommodation.name.asc())
    else:  # rating (по умолчанию)
        query = query.order_by(Accommodation.rating.desc())
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{accommodation_id}", response_model=AccommodationResponse)
async def get_accommodation_by_id(accommodation_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Accommodation)
        .where(Accommodation.id == accommodation_id)
        .where(Accommodation.is_active == True)
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Гостиница не найдена")
    return obj

@router.post("/", response_model=AccommodationResponse, status_code=status.HTTP_201_CREATED)
async def create_accommodation(
    accommodation_data: AccommodationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_obj = Accommodation(**accommodation_data.model_dump(), created_by=current_user.id)
    db.add(new_obj)
    await db.commit()
    await db.refresh(new_obj)
    return new_obj

@router.put("/{accommodation_id}", response_model=AccommodationResponse)
async def update_accommodation(
    accommodation_id: int,
    accommodation_data: AccommodationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Accommodation).where(Accommodation.id == accommodation_id))
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Гостиница не найдена")
    
    for key, value in accommodation_data.model_dump(exclude_unset=True).items():
        setattr(obj, key, value)
        
    await db.commit()
    await db.refresh(obj)
    return obj

@router.delete("/{accommodation_id}")
async def delete_accommodation(
    accommodation_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Accommodation).where(Accommodation.id == accommodation_id))
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Гостиница не найдена")
    
    obj.is_active = False
    await db.commit()
    return {"message": "Гостиница успешно удалена (скрыта)"}