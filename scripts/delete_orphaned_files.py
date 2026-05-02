import asyncio
import logging
import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from config import settings
import models

logger = logging.getLogger(__name__)

UPLOAD_DIR = Path("static/uploads/images")
DRY_RUN = False  # True = только просмотреть, False = реально удалить

engine = create_async_engine(settings.DATABASE_URL, echo=False)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

MODELS_WITH_IMAGES = [
    (models.Accommodation, "photo_url"),
    (models.Attraction, "photo_url"),
    (models.Event, "photo_url"),
    (models.Food, "photo_url"),
    (models.Souvenir, "photo_url"),
    (models.Route, "photo_url"),
    (models.User, "photo_url"),
    (models.PostcardTemplate, "image_url"),
]

async def run_cleanup():
    logger.info("Запуск очистки осиротевших файлов...")
    print("Запуск очистки осиротевших файлов...")
    print(f"Папка: {UPLOAD_DIR.absolute()}")
    print(f"Режим проверки (DRY_RUN): {DRY_RUN}")
    
    async with async_session_maker() as session:
        try:
            used_filenames = set()
            
            logger.info("Сканирование базы данных...")
            print("\nСканируем базу данных...")
            for model, column_name in MODELS_WITH_IMAGES:
                if not hasattr(model, column_name):
                    print(f"У модели {model.__name__} нет колонки {column_name}, пропускаем.")
                    continue
                    
                result = await session.execute(select(getattr(model, column_name)))
                urls = result.scalars().all()
                
                for url in urls:
                    if url:
                        filename = Path(url).name
                        used_filenames.add(filename)
            
            logger.info("Найдено %d уникальных файлов в БД.", len(used_filenames))
            print(f"Найдено {len(used_filenames)} уникальных файлов в БД.")

            if not UPLOAD_DIR.exists():
                logger.warning("Папка uploads не найдена: %s", UPLOAD_DIR.absolute())
                print("Папка uploads не найдена!")
                return

            disk_files = {
                f.name for f in UPLOAD_DIR.iterdir() 
                if f.is_file() and f.name not in {'.gitkeep', '.gitignore'}
            }
            logger.info("Найдено %d файлов на диске.", len(disk_files))
            print(f"Найдено {len(disk_files)} файлов на диске (без системных).")

            orphaned_files = disk_files - used_filenames
            
            if not orphaned_files:
                logger.info("Осиротевшие файлы не найдены.")
                print("\nВсё чисто! Осиротевших файлов нет.")
                return

            logger.warning("Найдено %d осиротевших файлов.", len(orphaned_files))
            print(f"\nНайдено {len(orphaned_files)} осиротевших файлов:")
            for filename in sorted(orphaned_files):
                file_path = UPLOAD_DIR / filename
                size_kb = file_path.stat().st_size / 1024
                print(f"   - {filename} ({size_kb:.1f} KB)")

            if not DRY_RUN:
                logger.info("Начинаю удаление файлов...")
                print("\nНачинаю удаление...")
                deleted_count = 0
                for filename in orphaned_files:
                    try:
                        file_path = UPLOAD_DIR / filename
                        os.remove(file_path)
                        deleted_count += 1
                        logger.info("Удалён файл: %s", filename)
                        print(f"Удалён: {filename}")
                    except Exception as e:
                        logger.error("Ошибка удаления %s: %s", filename, e)
                        print(f"Ошибка удаления {filename}: {e}")
                
                logger.info("Очистка завершена. Удалено файлов: %d", deleted_count)
                print(f"\nГотово! Удалено файлов: {deleted_count}")
            else:
                logger.info("Режим DRY_RUN активен. Файлы не удалены.")
                print("\nЧтобы реально удалить файлы, измени DRY_RUN = False в начале скрипта.")

        except Exception as e:
            logger.error("Критическая ошибка при выполнении скрипта: %s", e, exc_info=True)
            print(f"Ошибка при выполнении: {e}")
            raise
    
    logger.info("Скрипт завершён.")
    print("\nСкрипт завершён.")

if __name__ == "__main__":
    asyncio.run(run_cleanup())