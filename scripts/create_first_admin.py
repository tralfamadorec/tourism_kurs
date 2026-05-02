import asyncio
import os
import sys
import logging

# добавляем корень проекта в путь, чтобы работали импорты
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select

from database import async_session_maker
from models import User
from security import get_password_hash
from logging_config import setup_logging

logger = logging.getLogger(__name__)


async def create_admin():
    logger.info("Проверка наличия супер-администратора...")

    async with async_session_maker() as session:
        try:
            result = await session.execute(
                select(User).where(User.role == "super_admin")
            )
            existing_admin = result.scalar_one_or_none()

            if existing_admin:
                logger.info("Супер-администратор уже существует: %s", existing_admin.username)
                print(f"Супер-администратор уже существует: {existing_admin.username}")
                return

            logger.info("Создание нового супер-администратора...")

            username = (
                input("Введите имя пользователя (Enter для 'admin'): ") or "admin"
            )
            email = input("Введите email: ")
            password = input("Введите пароль: ")

            if not password:
                logger.warning("Пароль не может быть пустым.")
                print("Пароль не может быть пустым.")
                return

            new_admin = User(
                username=username,
                email=email,
                hashed_password=get_password_hash(password),
                role="super_admin",
                is_approved=True,
                is_active=True,
            )

            session.add(new_admin)
            await session.commit()

            logger.info("Супер-администратор создан: %s", username)
            print("\n" + "=" * 40)
            print("Готово! Супер-администратор создан.")
            print(f"Логин: {username}")
            print("=" * 40 + "\n")

        except Exception as e:
            logger.error("Ошибка при создании супер-администратора: %s", e, exc_info=True)
            print(f"Ошибка: {e}")
            await session.rollback()


if __name__ == "__main__":
    setup_logging()
    asyncio.run(create_admin())