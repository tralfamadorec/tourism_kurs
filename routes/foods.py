from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from database import get_db
from models import Food, User
from schemas import FoodCreate, FoodUpdate, FoodResponse
from security import get_current_user

router = APIRouter(prefix="/api/foods", tags=["Питание"])

@router.get("/", response_model=List[FoodResponse])
async def get_foods(
    limit: int = Query(50, ge=1, le=100),
    skip: int = Query(0, ge=0),
    cuisine: Optional[str] = Query(None, description="Фильтр по типу кухни"),
    location: Optional[str] = Query(None, description="Фильтр по населенному пункту"),
    accessibility: Optional[str] = Query(None, description="Фильтр по доступности"),
    sort: str = Query("rating", description="Сортировка: rating, avg_price, name"),
    db: AsyncSession = Depends(get_db)
):
    query = select(Food).where(Food.is_active == True)
    
    # фильтры
    if cuisine:
        query = query.where(Food.cuisine.ilike(f"%{cuisine}%"))
    if location:
        query = query.where(Food.address.ilike(f"%{location}%"))
    if accessibility == "accessible":
        query = query.where(Food.is_accessible == True)
    elif accessibility == "parking":
        query = query.where(Food.has_parking == True)
    
    # сортировка
    if sort == "avg_price":
        query = query.order_by(Food.avg_price.asc())
    elif sort == "name":
        query = query.order_by(Food.name.asc())
    else:
        query = query.order_by(Food.rating.desc())
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{food_id}", response_model=FoodResponse)
async def get_food_by_id(food_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Food)
        .where(Food.id == food_id)
        .where(Food.is_active == True)
    )
    obj = result.scalar_one_or_none()
    
    if not obj:
        raise HTTPException(status_code=404, detail="Заведение не найдено")
        
    return obj

@router.post("/", response_model=FoodResponse, status_code=status.HTTP_201_CREATED)
async def create_food(
    food_data: FoodCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_obj = Food(**food_data.model_dump())
    db.add(new_obj)
    await db.commit()
    await db.refresh(new_obj)
    return new_obj

@router.put("/{food_id}", response_model=FoodResponse)
async def update_food(
    food_id: int,
    food_data: FoodUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Food).where(Food.id == food_id))
    obj = result.scalar_one_or_none()
    
    if not obj:
        raise HTTPException(status_code=404, detail="Заведение не найдено")
    
    for key, value in food_data.model_dump(exclude_unset=True).items():
        setattr(obj, key, value)
        
    await db.commit()
    await db.refresh(obj)
    return obj

@router.delete("/{food_id}")
async def delete_food(
    food_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Food).where(Food.id == food_id))
    obj = result.scalar_one_or_none()
    
    if not obj:
        raise HTTPException(status_code=404, detail="Заведение не найдено")
    
    obj.is_active = False
    await db.commit()
    
    return {"message": "Заведение удалено"}