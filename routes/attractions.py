from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from database import get_db
from models import Attraction, User
from schemas import AttractionCreate, AttractionResponse, AttractionUpdate
from security import get_current_user

router = APIRouter(prefix="/api/attractions", tags=["Достопримечатльности"])

@router.get("/", response_model=List[AttractionResponse])
async def get_attractions(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Attraction).where(Attraction.is_active == True))
    attractions = result.scalars().all()
    return attractions

@router.get("/{attraction_id}", response_model=AttractionResponse)
async def get_attraction_by_id(attraction_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Attraction)
        .where(Attraction.id == attraction_id)
        .where(Attraction.is_active == True)  # ← Добавили эту строку!
    )
    attraction = result.scalar_one_or_none()

    if not attraction:
        raise HTTPException(status_code=404, detail="Достопримечательность не найдена")
    return attraction

@router.post("/", response_model=AttractionResponse, status_code=status.HTTP_201_CREATED)
async def create_attraction(
    attraction_data: AttractionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_attraction = Attraction(
        **attraction_data.model_dump(),
        created_by=current_user.id
    )
    db.add(new_attraction)
    await db.commit()
    await db.refresh(new_attraction)
    return new_attraction

@router.put("/{attraction_id}", response_model=AttractionResponse)
async def update_attraction(
    attraction_id: int, 
    attraction_data: AttractionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Attraction).where(Attraction.id == attraction_id))
    attraction = result.scalar_one_or_none()
    
    if not attraction:
        raise HTTPException(status_code=404, detail="Объект не найден")
    
    update_data = attraction_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(attraction, key, value)
        
    await db.commit()
    await db.refresh(attraction)
    return attraction

@router.delete("/{attraction_id}")
async def delete_attraction(
    attraction_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Attraction).where(Attraction.id == attraction_id))
    attraction = result.scalar_one_or_none()
    
    if not attraction:
        raise HTTPException(status_code=404, detail="Объект не найден")
    
    attraction.is_active = False
    await db.commit()
    
    return {"message": "Достопримечательность успешно удалена (скрыта)"}