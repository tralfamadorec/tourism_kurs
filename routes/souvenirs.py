from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from database import get_db
from models import Souvenir
from schemas import SouvenirCreate, SouvenirUpdate, SouvenirResponse
from security import get_current_user
from models import User

router = APIRouter(prefix="/api/souvenirs", tags=["Сувениры"])

@router.get("/", response_model=List[SouvenirResponse])
async def get_souvenirs(
    limit: int = Query(50, ge=1, le=100),
    skip: int = Query(0, ge=0),
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None),  # Тип магазина
    sort: str = Query("name", description="name, category"),
    db: AsyncSession = Depends(get_db)
):
    query = select(Souvenir).where(Souvenir.is_active == True)
    
    if search:
        query = query.where(Souvenir.name.ilike(f"%{search}%"))
    if category:
        query = query.where(Souvenir.category.ilike(f"%{category}%"))
        
    if sort == "category":
        query = query.order_by(Souvenir.category.asc(), Souvenir.name.asc())
    else:
        query = query.order_by(Souvenir.name.asc())
        
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()
@router.get("/{souvenir_id}", response_model=SouvenirResponse)
async def get_souvenir_by_id(souvenir_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Souvenir)
        .where(Souvenir.id == souvenir_id)
        .where(Souvenir.is_active == True)
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Сувенир не найден")
    return obj

@router.post("/", response_model=SouvenirResponse, status_code=status.HTTP_201_CREATED)
async def create_souvenir(
    souvenir_data: SouvenirCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_obj = Souvenir(**souvenir_data.model_dump(), created_by=current_user.id)
    db.add(new_obj)
    await db.commit()
    await db.refresh(new_obj)
    return new_obj

@router.put("/{souvenir_id}", response_model=SouvenirResponse)
async def update_souvenir(
    souvenir_id: int,
    souvenir_data: SouvenirUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Souvenir).where(Souvenir.id == souvenir_id))
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Сувенир не найден")
    
    for key, value in souvenir_data.model_dump(exclude_unset=True).items():
        setattr(obj, key, value)
        
    await db.commit()
    await db.refresh(obj)
    return obj

@router.delete("/{souvenir_id}")
async def delete_souvenir(
    souvenir_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Souvenir).where(Souvenir.id == souvenir_id))
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Сувенир не найден")
    
    obj.is_active = False
    await db.commit()
    return {"message": "Сувенир успешно удален (скрыт)"}