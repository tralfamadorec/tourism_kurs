import logging
from fastapi import Depends, HTTPException, Request, status
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from database import get_db
from models import User

logger = logging.getLogger(__name__)


async def require_admin_auth(request: Request, db: AsyncSession = Depends(get_db)):
    # зависимость для защиты админ-страниц: проверяет токен и роль пользователя
    token = request.cookies.get("access_token")

    if not token:
        logger.warning("Попытка доступа к админ-странице без токена: %s", request.url.path)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Необходима авторизация"
        )

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")

        if username:
            result = await db.execute(select(User).where(User.username == username))
            current_user = result.scalar_one_or_none()

            if current_user:
                # проверка роли: только admin или super_admin
                if current_user.role not in ["admin", "super_admin"]:
                    logger.warning("Отказано в доступе к админ-панели. Пользователь: %s, Роль: %s", current_user.username, current_user.role)
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Доступ запрещён: недостаточно прав",
                    )
                return current_user

    except JWTError:
        logger.warning("Недействительный JWT токен при доступе к админ-странице")
        pass

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный токен"
    )