import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import User
from schemas import ResetPasswordRequest, UserResponse, UserRoleUpdate
from security import get_current_user, get_password_hash, require_role

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin/users", tags=["Управление пользователями"])


@router.get("/", response_model=list[UserResponse])
async def get_all_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("super_admin")),
):
    result = await db.execute(select(User).order_by(User.id.desc()))
    logger.info("Запрошен список всех пользователей")
    return result.scalars().all()


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user_role(
    user_id: int,
    update_data: UserRoleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("super_admin")),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        logger.warning("Пользователь не найден для обновления: id=%d", user_id)
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    if user.id == current_user.id and update_data.role != "super_admin":
        raise HTTPException(
            status_code=400, detail="Нельзя понизить собственную роль super_admin"
        )

    user.role = update_data.role
    user.is_approved = update_data.is_approved
    if update_data.is_active is not None:
        user.is_active = update_data.is_active

    await db.commit()
    await db.refresh(user)
    logger.info("Роль пользователя обновлена: user_id=%d, role=%s", user_id, user.role)
    return user


@router.post("/{user_id}/reset-password")
async def reset_user_password(
    user_id: int,
    password_data: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("super_admin")),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        logger.warning("Попытка сброса пароля для несуществующего пользователя: id=%d", user_id)
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    user.hashed_password = get_password_hash(password_data.new_password)
    await db.commit()
    logger.info("Пароль пользователя сброшен: user_id=%d", user_id)

    return {"message": "Пароль успешно сброшен"}


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("super_admin")),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        logger.warning("Попытка удаления несуществующего пользователя: id=%d", user_id)
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    if user.id == current_user.id:
        raise HTTPException(
            status_code=400, detail="Нельзя удалить собственную учётную запись"
        )

    await db.delete(user)
    await db.commit()
    logger.info("Пользователь удален: user_id=%d", user_id)