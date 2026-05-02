import logging
from datetime import timedelta

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from database import get_db
from security import authenticate_user, create_access_token

logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/")
def home(request: Request):
    return templates.TemplateResponse(request, "index.html", {"request": request})


@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html", {"request": request})


@router.post("/login")
async def login_post(
    username: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    user = await authenticate_user(username, password, db)
    if not user or not user.is_approved or not user.is_active:
        logger.warning("Неудачная попытка входа: %s", username)
        raise HTTPException(status_code=400, detail="Неверные данные")

    token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    logger.info("Успешный вход: %s", username)
    response = RedirectResponse(url="/admin", status_code=302)
    response.set_cookie(key="access_token", value=token, httponly=True)
    return response


@router.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse(request, "register.html", {"request": request})


@router.get("/food")
def food_page(request: Request):
    return templates.TemplateResponse(request, "food.html", {"request": request})


@router.get("/routes")
def routes_page(request: Request):
    return templates.TemplateResponse(request, "routes.html", {"request": request})


@router.get("/attractions")
def attractions_page(request: Request):
    return templates.TemplateResponse(request, "attractions.html", {"request": request})


@router.get("/accommodations")
def accommodations_page(request: Request):
    return templates.TemplateResponse(
        request, "accommodations.html", {"request": request}
    )


@router.get("/events")
def events_page(request: Request):
    return templates.TemplateResponse(request, "events.html", {"request": request})


@router.get("/safety")
def safety_page(request: Request):
    return templates.TemplateResponse(request, "safety.html", {"request": request})


@router.get("/safety_memos")
def safety_memos_page(request: Request):
    return templates.TemplateResponse(
        request, "safety_memos.html", {"request": request}
    )


@router.get("/souvenirs")
def souvenirs_page(request: Request):
    return templates.TemplateResponse(request, "souvenirs.html", {"request": request})


@router.get("/postcards")
def postcards_page(request: Request):
    return templates.TemplateResponse(request, "postcards.html", {"request": request})


@router.get("/map")
def map_page(request: Request):
    return templates.TemplateResponse(
        request,
        "map.html",
        {"request": request, "yandex_api_key": settings.YANDEX_MAPS_API_KEY},
    )


@router.get("/contacts")
def contacts_page(request: Request):
    return templates.TemplateResponse(request, "contacts.html", {"request": request})


@router.get("/inclusive")
def inclusive_page(request: Request):
    return templates.TemplateResponse(request, "inclusive.html", {"request": request})