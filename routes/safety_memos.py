import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import SafetyMemo, User
from schemas import SafetyMemoCreate, SafetyMemoResponse, SafetyMemoUpdate
from security import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/safety/memos", tags=["Памятки безопасности"])


@router.get("/", response_model=List[SafetyMemoResponse])
async def get_safety_memos(
    limit: int = Query(50, ge=1, le=100),
    skip: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    query = select(SafetyMemo).where(SafetyMemo.is_active == True)
    query = query.order_by(SafetyMemo.order).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.post(
    "/", response_model=SafetyMemoResponse, status_code=status.HTTP_201_CREATED
)
async def create_safety_memo(
    memo_data: SafetyMemoCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    logger.info("Создание памятки безопасности: %s (user: %s)", memo_data.title, current_user.username)
    new_memo = SafetyMemo(**memo_data.model_dump())
    db.add(new_memo)
    await db.commit()
    await db.refresh(new_memo)
    logger.info("Памятка безопасности создана: id=%d", new_memo.id)
    return new_memo


@router.get("/{memo_id}", response_model=SafetyMemoResponse)
async def get_safety_memo_by_id(memo_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SafetyMemo).where(SafetyMemo.id == memo_id))
    memo = result.scalar_one_or_none()

    if not memo:
        logger.warning("Памятка не найдена: id=%d", memo_id)
        raise HTTPException(status_code=404, detail="Памятка не найдена")

    return memo


@router.put("/{memo_id}", response_model=SafetyMemoResponse)
async def update_safety_memo(
    memo_id: int,
    memo_data: SafetyMemoUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(SafetyMemo).where(SafetyMemo.id == memo_id))
    memo = result.scalar_one_or_none()

    if not memo:
        logger.warning("Памятка не найдена для обновления: id=%d", memo_id)
        raise HTTPException(status_code=404, detail="Памятка не найдена")

    logger.info("Обновление памятки безопасности: id=%d (user: %s)", memo_id, current_user.username)
    for key, value in memo_data.model_dump(exclude_unset=True).items():
        setattr(memo, key, value)

    await db.commit()
    await db.refresh(memo)
    logger.info("Памятка безопасности обновлена: id=%d", memo.id)
    return memo


@router.delete("/{memo_id}")
async def delete_safety_memo(
    memo_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(SafetyMemo).where(SafetyMemo.id == memo_id))
    memo = result.scalar_one_or_none()

    if not memo:
        logger.warning("Памятка не найдена для удаления: id=%d", memo_id)
        raise HTTPException(status_code=404, detail="Памятка не найдена")

    logger.info("Удаление памятки безопасности: id=%d (user: %s)", memo_id, current_user.username)
    memo.is_active = False
    await db.commit()
    logger.info("Памятка безопасности скрыта: id=%d", memo.id)

    return {"message": "Памятка скрыта"}