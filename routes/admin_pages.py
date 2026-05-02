import logging
from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from database import get_db
from dependencies import require_admin_auth
from models import User

logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="templates")


# темы
@router.get("/admin", dependencies=[Depends(require_admin_auth)])
async def admin_dashboard(request: Request, db: AsyncSession = Depends(get_db)):
    token = request.cookies.get("access_token")
    current_user = None
    if token:
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            username: str = payload.get("sub")
            if username:
                result = await db.execute(select(User).where(User.username == username))
                current_user = result.scalar_one_or_none()
        except JWTError:
            pass
    logger.info("Admin dashboard accessed")
    return templates.TemplateResponse(
        request,
        "admin/base_admin.html",
        {"request": request, "current_user": current_user},
    )


@router.get("/admin/profile", dependencies=[Depends(require_admin_auth)])
def admin_profile(request: Request):
    return templates.TemplateResponse(
        request, "admin/profile.html", {"request": request}
    )


@router.get("/admin/themes", dependencies=[Depends(require_admin_auth)])
def admin_themes(request: Request):
    return templates.TemplateResponse(
        request, "admin/themes.html", {"request": request}
    )


# достопримечательности
@router.get("/admin/attractions", dependencies=[Depends(require_admin_auth)])
def admin_attractions_list(request: Request):
    return templates.TemplateResponse(
        request, "admin/attractions_list.html", {"request": request}
    )


@router.get("/admin/attractions/new", dependencies=[Depends(require_admin_auth)])
def admin_attractions_new(request: Request):
    return templates.TemplateResponse(
        request,
        "admin/attractions_form.html",
        {
            "request": request,
            "title": "Добавить достопримечательность",
            "back_url": "/admin/attractions",
            "api_path": "/attractions",
            "is_edit": False,
        },
    )


@router.get(
    "/admin/attractions/{item_id}/edit", dependencies=[Depends(require_admin_auth)]
)
def admin_attractions_edit(request: Request, item_id: int):
    return templates.TemplateResponse(
        request,
        "admin/attractions_form.html",
        {
            "request": request,
            "title": "Редактировать достопримечательность",
            "back_url": "/admin/attractions",
            "is_edit": True,
            "item_id": item_id,
        },
    )


# маршруты
@router.get("/admin/routes", dependencies=[Depends(require_admin_auth)])
def admin_routes_list(request: Request):
    return templates.TemplateResponse(
        request, "admin/routes_list.html", {"request": request}
    )


@router.get("/admin/routes/new", dependencies=[Depends(require_admin_auth)])
def admin_routes_new(request: Request):
    return templates.TemplateResponse(
        request,
        "admin/routes_form.html",
        {
            "request": request,
            "title": "Новый маршрут",
            "back_url": "/admin/routes",
            "api_path": "/routes",
            "is_edit": False,
            "item": None,
        },
    )


@router.get("/admin/routes/{item_id}/edit", dependencies=[Depends(require_admin_auth)])
def admin_routes_edit(request: Request, item_id: int):
    return templates.TemplateResponse(
        request,
        "admin/routes_form.html",
        {
            "request": request,
            "title": "Редактировать маршрут",
            "back_url": "/admin/routes",
            "is_edit": True,
            "item_id": item_id,
        },
    )


# гостиницы
@router.get("/admin/hotels", dependencies=[Depends(require_admin_auth)])
def admin_hotels_list(request: Request):
    return templates.TemplateResponse(
        request, "admin/hotels_list.html", {"request": request}
    )


@router.get("/admin/hotels/new", dependencies=[Depends(require_admin_auth)])
def admin_hotels_new(request: Request):
    return templates.TemplateResponse(
        request,
        "admin/hotels_form.html",
        {
            "request": request,
            "title": "Новая гостиница",
            "back_url": "/admin/hotels",
            "is_edit": False,
            "item_id": None,
        },
    )


@router.get("/admin/hotels/{item_id}/edit", dependencies=[Depends(require_admin_auth)])
def admin_hotels_edit(request: Request, item_id: int):
    return templates.TemplateResponse(
        request,
        "admin/hotels_form.html",
        {
            "request": request,
            "title": "Редактировать гостиницу",
            "back_url": "/admin/hotels",
            "is_edit": True,
            "item_id": item_id,
        },
    )


# рестораны
@router.get("/admin/foods", dependencies=[Depends(require_admin_auth)])
def admin_food_list(request: Request):
    return templates.TemplateResponse(
        request, "admin/foods_list.html", {"request": request}
    )


@router.get("/admin/foods/new", dependencies=[Depends(require_admin_auth)])
def admin_food_new(request: Request):
    return templates.TemplateResponse(
        request,
        "admin/foods_form.html",
        {
            "request": request,
            "title": "Новое заведение",
            "back_url": "/admin/food",
            "is_edit": False,
            "item_id": None,
        },
    )


@router.get("/admin/foods/{item_id}/edit", dependencies=[Depends(require_admin_auth)])
async def admin_food_edit(request: Request, item_id: int):
    return templates.TemplateResponse(
        request,
        "admin/foods_form.html",
        {
            "request": request,
            "title": "Редактировать заведение",
            "back_url": "/admin/food",
            "is_edit": True,
            "item_id": item_id,
        },
    )


# события
@router.get("/admin/events", dependencies=[Depends(require_admin_auth)])
def admin_events_list(request: Request):
    return templates.TemplateResponse(
        request, "admin/events_list.html", {"request": request}
    )


@router.get("/admin/events/new", dependencies=[Depends(require_admin_auth)])
def admin_events_new(request: Request):
    return templates.TemplateResponse(
        request,
        "admin/events_form.html",
        {
            "request": request,
            "title": "Новое событие",
            "back_url": "/admin/events",
            "is_edit": False,
            "item_id": None,
        },
    )


@router.get("/admin/events/{item_id}/edit", dependencies=[Depends(require_admin_auth)])
def admin_events_edit(request: Request, item_id: int):
    return templates.TemplateResponse(
        request,
        "admin/events_form.html",
        {
            "request": request,
            "title": "Редактировать событие",
            "back_url": "/admin/events",
            "is_edit": True,
            "item_id": item_id,
        },
    )


# сувениры
@router.get("/admin/souvenirs", dependencies=[Depends(require_admin_auth)])
def admin_souvenirs_list(request: Request):
    return templates.TemplateResponse(
        request, "admin/souvenirs_list.html", {"request": request}
    )


@router.get("/admin/souvenirs/new", dependencies=[Depends(require_admin_auth)])
def admin_souvenirs_new(request: Request):
    return templates.TemplateResponse(
        request,
        "admin/souvenirs_form.html",
        {
            "request": request,
            "title": "Новый сувенир",
            "back_url": "/admin/souvenirs",
            "is_edit": False,
            "item_id": None,
        },
    )


@router.get(
    "/admin/souvenirs/{item_id}/edit", dependencies=[Depends(require_admin_auth)]
)
def admin_souvenirs_edit(request: Request, item_id: int):
    return templates.TemplateResponse(
        request,
        "admin/souvenirs_form.html",
        {
            "request": request,
            "title": "Редактировать сувенир",
            "back_url": "/admin/souvenirs",
            "is_edit": True,
            "item_id": item_id,
        },
    )


# безопасность
@router.get("/admin/safety", dependencies=[Depends(require_admin_auth)])
def admin_safety_list(request: Request):
    return templates.TemplateResponse(
        request, "admin/safety_list.html", {"request": request}
    )


@router.get("/admin/safety/new", dependencies=[Depends(require_admin_auth)])
def admin_safety_new(request: Request):
    return templates.TemplateResponse(
        request,
        "admin/safety_form.html",
        {
            "request": request,
            "title": "Новая запись",
            "back_url": "/admin/safety",
            "is_edit": False,
            "item_id": None,
        },
    )


@router.get("/admin/safety/{item_id}/edit", dependencies=[Depends(require_admin_auth)])
def admin_safety_edit(request: Request, item_id: int):
    return templates.TemplateResponse(
        request,
        "admin/safety_form.html",
        {
            "request": request,
            "title": "Редактировать запись",
            "back_url": "/admin/safety",
            "is_edit": True,
            "item_id": item_id,
        },
    )


# памятки
@router.get("/admin/memos", dependencies=[Depends(require_admin_auth)])
def admin_memos_list(request: Request):
    return templates.TemplateResponse(
        request, "admin/safety_list.html", {"request": request}
    )


@router.get("/admin/memos/new", dependencies=[Depends(require_admin_auth)])
def admin_memo_new(request: Request):
    return templates.TemplateResponse(
        request,
        "admin/memos_form.html",
        {
            "request": request,
            "title": "Новая памятка",
            "back_url": "/admin/memos",
            "is_edit": False,
            "item_id": None,
        },
    )


@router.get("/admin/memos/{memo_id}/edit", dependencies=[Depends(require_admin_auth)])
def admin_memo_edit(request: Request, memo_id: int):
    return templates.TemplateResponse(
        request,
        "admin/memos_form.html",
        {
            "request": request,
            "title": "Редактировать памятку",
            "back_url": "/admin/memos",
            "is_edit": True,
            "item_id": memo_id,
        },
    )


# открытки
@router.get("/admin/postcards", dependencies=[Depends(require_admin_auth)])
def admin_postcards_list(request: Request):
    return templates.TemplateResponse(
        request, "admin/postcards_list.html", {"request": request}
    )


@router.get("/admin/postcards/new", dependencies=[Depends(require_admin_auth)])
def admin_postcards_new(request: Request):
    return templates.TemplateResponse(
        request,
        "admin/postcards_form.html",
        {
            "request": request,
            "title": "Новый шаблон открытки",
            "back_url": "/admin/postcards",
            "is_edit": False,
            "item_id": None,
        },
    )


@router.get(
    "/admin/postcards/{item_id}/edit", dependencies=[Depends(require_admin_auth)]
)
def admin_postcards_edit(request: Request, item_id: int):
    return templates.TemplateResponse(
        request,
        "admin/postcards_form.html",
        {
            "request": request,
            "title": "Редактировать шаблон",
            "back_url": "/admin/postcards",
            "is_edit": True,
            "item_id": item_id,
        },
    )


# пользователи
@router.get("/admin/users", dependencies=[Depends(require_admin_auth)])
def admin_users_list(request: Request):
    token = request.cookies.get("access_token")
    current_user_id = None
    if token:
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            current_user_id = payload.get("user_id")
        except JWTError:
            pass
    logger.info("Admin users list accessed")
    return templates.TemplateResponse(
        request,
        "admin/users_list.html",
        {"request": request, "current_user_id": current_user_id},
    )