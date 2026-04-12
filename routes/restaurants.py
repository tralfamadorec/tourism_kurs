from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from database import get_db
from models import Restaurant
from schemas import RestaurantCreate, RestaurantUpdate, RestaurantResponse
from security import get_current_user
from models import User

router = APIRouter(prefix="/api/restaurants", tags=["Рестораны"])

@router.get("/", response_model=List[RestaurantResponse])
async def get_restaurants(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Restaurant).where(Restaurant.is_active == True))
    return result.scalars().all()

@router.get("/{restaurant_id}", response_model=RestaurantResponse)
async def get_restaurant_by_id(restaurant_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Restaurant)
        .where(Restaurant.id == restaurant_id)
        .where(Restaurant.is_active == True)
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Ресторан не найден")
    return obj

@router.post("/", response_model=RestaurantResponse, status_code=status.HTTP_201_CREATED)
async def create_restaurant(
    restaurant_data: RestaurantCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_obj = Restaurant(**restaurant_data.model_dump(), created_by=current_user.id)
    db.add(new_obj)
    await db.commit()
    await db.refresh(new_obj)
    return new_obj

@router.put("/{restaurant_id}", response_model=RestaurantResponse)
async def update_restaurant(
    restaurant_id: int,
    restaurant_data: RestaurantUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Restaurant).where(Restaurant.id == restaurant_id))
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Ресторан не найден")
    
    for key, value in restaurant_data.model_dump(exclude_unset=True).items():
        setattr(obj, key, value)
        
    await db.commit()
    await db.refresh(obj)
    return obj

@router.delete("/{restaurant_id}")
async def delete_restaurant(
    restaurant_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Restaurant).where(Restaurant.id == restaurant_id))
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Ресторан не найден")
    
    obj.is_active = False
    await db.commit()
    return {"message": "Ресторан успешно удален (скрыт)"}