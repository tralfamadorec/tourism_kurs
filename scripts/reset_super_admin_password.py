import asyncio
import logging
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select

from database import get_db
from models import User
from security import get_password_hash
from logging_config import setup_logging

logger = logging.getLogger(__name__)


async def reset_super_admin_password(new_password: str = None):
    logger.info("Запуск скрипта сброса пароля супер-администратора")

    if not new_password:
        import secrets

        new_password = secrets.token_urlsafe(12)
        logger.info("Сгенерирован случайный пароль")
        print(f"\nСгенерирован случайный пароль: {new_password}\n")

    async for db in get_db():
        try:
            result = await db.execute(
                select(User).where(User.role == "super_admin").order_by(User.id)
            )
            admin = result.scalar_one_or_none()

            if not admin:
                logger.warning("Супер-админ не найден в базе данных")
                print("Супер-админ не найден в базе данных!")
                return

            admin.hashed_password = get_password_hash(new_password)
            await db.commit()

            logger.info("Пароль успешно сброшен для пользователя: %s", admin.username)
            print("Пароль успешно сброшен!")
            print(f"Логин: {admin.username}")
            print(f"Новый пароль: {new_password}")
            print("\nСмените пароль сразу после входа!\n")
            break
        except Exception as e:
            logger.error("Ошибка при сбросе пароля: %s", e, exc_info=True)
            print(f"Ошибка: {e}")
            await db.rollback()
            return


if __name__ == "__main__":
    setup_logging()
    password = sys.argv[1] if len(sys.argv) > 1 else None
    asyncio.run(reset_super_admin_password(password))