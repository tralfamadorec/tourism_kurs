from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from database import get_db
from models import Route
from schemas import RouteCreate, RouteUpdate, RouteResponse
from security import get_current_user
from models import User

router = APIRouter(prefix="/api/routes", tags=["Маршруты"])

@router.get("/", response_model=List[RouteResponse])
async def get_routes(
    skip: int = Query(0, ge=0, description="Пропустить N записей"),
    limit: int = Query(20, ge=1, le=100, description="Вернуть не более N записей"),
    db: AsyncSession = Depends(get_db)
):
    query = select(Route).where(Route.is_active == True).order_by(Route.title.asc())
    
    count_query = select(func.count(Route.id)).where(Route.is_active == True)
    total = await db.scalar(count_query)
    
    result = await db.execute(query.offset(skip).limit(limit))
    return result.scalars().all()

@router.get("/{route_id}", response_model=RouteResponse)
async def get_route_by_id(route_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Route).where(Route.id == route_id).where(Route.is_active == True)
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Маршрут не найден")
    return obj

@router.post("/", response_model=RouteResponse, status_code=status.HTTP_201_CREATED)
async def create_route(
    route_data: RouteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_obj = Route(**route_data.model_dump(), created_by=current_user.id)
    db.add(new_obj)
    await db.commit()
    await db.refresh(new_obj)
    return new_obj

@router.put("/{route_id}", response_model=RouteResponse)
async def update_route(
    route_id: int,
    route_data: RouteUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Route).where(Route.id == route_id))
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Маршрут не найден")
    
    for key, value in route_data.model_dump(exclude_unset=True).items():
        setattr(obj, key, value)
        
    await db.commit()
    await db.refresh(obj)
    return obj

@router.delete("/{route_id}")
async def delete_route(
    route_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Route).where(Route.id == route_id))
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Маршрут не найден")
    
    obj.is_active = False
    await db.commit()
    return {"message": "Маршрут успешно удалён (скрыт)"}