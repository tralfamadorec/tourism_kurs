import logging
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import (Accommodation, Attraction, Event, Food, Route, SafetyObject, Souvenir)

logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/attractions/{item_id}")
async def attraction_detail(
    request: Request, item_id: int, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Attraction).where(Attraction.id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        logger.warning("Достопримечательность не найдена: id=%d", item_id)
        raise HTTPException(404, "Объект не найден")
    logger.debug("Показана страница достопримечательности: id=%d", item_id)
    return templates.TemplateResponse(
        request,
        "object_detail.html",
        {
            "request": request,
            "item": item,
            "title": item.name,
            "back_url": "/attractions",
            "details": [
                ("Адрес", item.address),
                ("Рейтинг", f"{item.rating} из 5" if item.rating else None),
                ("Доступно для МГН", "Да" if item.is_accessible else None),
            ],
            "objType": "attraction",
            "description": item.description,
            "photo": item.photo_url,
        },
    )


@router.get("/hotels/{item_id}")
async def hotel_detail(
    request: Request, item_id: int, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Accommodation).where(Accommodation.id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        logger.warning("Гостиница не найдена: id=%d", item_id)
        raise HTTPException(404, "Гостиница не найдена")
    logger.debug("Показана страница гостиницы: id=%d", item_id)
    return templates.TemplateResponse(
        request,
        "object_detail.html",
        {
            "request": request,
            "item": item,
            "title": item.name,
            "back_url": "/accommodations",
            "details": [
                ("Адрес", item.address),
                ("Телефон", item.phone),
                ("Сайт", item.website),
                (
                    "Цена за ночь",
                    f"{item.price_per_night} ₽" if item.price_per_night else None,
                ),
                ("Рейтинг", f"{item.rating} из 5" if item.rating else None),
                ("Доступно для МГН", "Да" if item.is_accessible else None),
            ],
            "objType": "accommodation",
            "description": item.description,
            "photo": item.photo_url,
        },
    )


@router.get("/food/{item_id}")
async def food_detail(
    request: Request, item_id: int, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Food).where(Food.id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        logger.warning("Заведение не найдено: id=%d", item_id)
        raise HTTPException(404, "Заведение не найдено")
    logger.debug("Показана страница заведения: id=%d", item_id)
    return templates.TemplateResponse(
        request,
        "object_detail.html",
        {
            "request": request,
            "item": item,
            "title": item.name,
            "back_url": "/food",
            "details": [
                ("Адрес", item.address),
                ("Телефон", item.phone),
                ("Кухня", item.cuisine),
                ("Средний чек", f"{item.avg_price} ₽" if item.avg_price else None),
                ("Рейтинг", f"{item.rating} из 5" if item.rating else None),
                ("Доступно для МГН", "Да" if item.is_accessible else None),
            ],
            "objType": "food",
            "description": item.description,
            "photo": item.photo_url,
        },
    )


@router.get("/events/{item_id}")
async def event_detail(
    request: Request, item_id: int, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Event).where(Event.id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        logger.warning("Событие не найдено: id=%d", item_id)
        raise HTTPException(404, "Событие не найдено")
    logger.debug("Показана страница события: id=%d", item_id)
    return templates.TemplateResponse(
        request,
        "object_detail.html",
        {
            "request": request,
            "item": item,
            "title": item.title,
            "back_url": "/events",
            "details": [
                (
                    "Дата и время",
                    (
                        item.event_date.strftime("%d.%m.%Y %H:%M")
                        if item.event_date
                        else None
                    ),
                ),
                ("Место проведения", item.location),
                ("Категория", item.category),
                ("Доступно для МГН", "Да" if item.is_accessible else None),
            ],
            "objType": "event",
            "description": item.description,
            "photo": item.photo_url,
        },
    )


@router.get("/routes/{item_id}")
async def route_detail(
    request: Request, item_id: int, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Route).where(Route.id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        logger.warning("Маршрут не найден: id=%d", item_id)
        raise HTTPException(404, "Маршрут не найден")
    logger.debug("Показана страница маршрута: id=%d", item_id)
    return templates.TemplateResponse(
        request,
        "object_detail.html",
        {
            "request": request,
            "item": item,
            "title": item.title,
            "back_url": "/routes",
            "details": [
                (
                    "Длительность",
                    f"{item.duration_hours} ч." if item.duration_hours else None,
                ),
                ("Сложность", item.difficulty),
                ("Транспорт", item.transport_type),
                ("Доступно для МГН", "Да" if item.is_accessible else None),
            ],
            "objType": "route",
            "description": item.description,
            "photo": item.photo_url,
        },
    )


@router.get("/safety/{item_id}")
async def safety_detail(
    request: Request, item_id: int, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(SafetyObject).where(SafetyObject.id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        logger.warning("Объект безопасности не найден: id=%d", item_id)
        raise HTTPException(404, "Объект не найден")
    logger.debug("Показана страница объекта безопасности: id=%d", item_id)
    return templates.TemplateResponse(
        request,
        "object_detail.html",
        {
            "request": request,
            "item": item,
            "title": item.name,
            "back_url": "/safety",
            "details": [
                ("Категория", item.category),
                ("Адрес", item.address),
                ("Телефон", item.phone),
            ],
            "objType": "safety",
            "description": None,
            "photo": None,
        },
    )


@router.get("/souvenirs/{item_id}")
async def souvenir_detail(
    request: Request, item_id: int, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Souvenir).where(Souvenir.id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        logger.warning("Сувенир не найден: id=%d", item_id)
        raise HTTPException(404, "Сувенир не найден")
    logger.debug("Показана страница сувенира: id=%d", item_id)
    return templates.TemplateResponse(
        request,
        "object_detail.html",
        {
            "request": request,
            "item": item,
            "title": item.name,
            "back_url": "/souvenirs",
            "details": [
                ("Категория", item.category),
                ("Доступно для МГН", "Да" if item.is_accessible else None),
            ],
            "objType": "souvenir",
            "description": item.description,
            "photo": item.photo_url,
        },
    )