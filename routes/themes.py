import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import SiteSetting, User
from schemas import ThemeResponse, ThemeUpdate
from security import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/themes", tags=["Настройки сайта"])


@router.get("/active", response_model=ThemeResponse)
async def get_active_theme(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(SiteSetting).where(SiteSetting.key == "active_theme")
    )
    setting = result.scalar_one_or_none()

    if not setting:
        new_setting = SiteSetting(key="active_theme", value="default")
        db.add(new_setting)
        await db.commit()
        logger.info("Создана настройка темы по умолчанию: default")
        return {"active_theme": "default"}

    logger.debug("Получена активная тема: %s", setting.value)
    return {"active_theme": setting.value}


@router.patch("/active", response_model=ThemeResponse)
async def set_active_theme(
    data: ThemeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    logger.info("Попытка смены темы пользователем: %s, Роль: %s", current_user.username, current_user.role)

    if current_user.role not in ["admin", "super_admin"]:
        logger.warning("Отказано в доступе к смене темы. Роль: %s", current_user.role)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Ваша роль {current_user.role} не имеет доступа",
        )

    result = await db.execute(
        select(SiteSetting).where(SiteSetting.key == "active_theme")
    )
    setting = result.scalar_one_or_none()

    if setting:
        setting.value = data.active_theme
        logger.info("Тема обновлена на: %s", data.active_theme)
    else:
        new_setting = SiteSetting(key="active_theme", value=data.active_theme)
        db.add(new_setting)
        logger.info("Создана новая настройка темы: %s", data.active_theme)

    await db.commit()
    return {"active_theme": data.active_theme}