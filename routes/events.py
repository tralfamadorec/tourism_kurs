from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime

from database import get_db
from models import Event
from schemas import EventCreate, EventUpdate, EventResponse
from security import get_current_user
from models import User

router = APIRouter(prefix="/api/events", tags=["События"])

@router.get("/", response_model=List[EventResponse])
async def get_events(
    date_from: Optional[datetime] = Query(None, description="Фильтр: события от даты"),
    date_to: Optional[datetime] = Query(None, description="Фильтр: события до даты"),
    db: AsyncSession = Depends(get_db)
):
    query = select(Event).where(Event.is_active == True)
    
    if date_from:
        query = query.where(Event.event_date >= date_from)
    if date_to:
        query = query.where(Event.event_date <= date_to)
        
    result = await db.execute(query.order_by(Event.event_date.asc()))
    return result.scalars().all()

@router.get("/{event_id}", response_model=EventResponse)
async def get_event_by_id(event_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Event).where(Event.id == event_id).where(Event.is_active == True)
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Событие не найдено")
    return obj

@router.post("/", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(
    event_data: EventCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_obj = Event(**event_data.model_dump(), created_by=current_user.id)
    db.add(new_obj)
    await db.commit()
    await db.refresh(new_obj)
    return new_obj

@router.put("/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: int,
    event_data: EventUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Event).where(Event.id == event_id))
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Событие не найдено")
    
    for key, value in event_data.model_dump(exclude_unset=True).items():
        setattr(obj, key, value)
        
    await db.commit()
    await db.refresh(obj)
    return obj

@router.delete("/{event_id}")
async def delete_event(
    event_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Event).where(Event.id == event_id))
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Событие не найдено")
    
    obj.is_active = False
    await db.commit()
    return {"message": "Событие успешно удалено (скрыта)"}