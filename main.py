from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
import os
import httpx
import logging
from fastapi import HTTPException

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database import Base, get_db, engine

from fastapi import UploadFile, File
from pathlib import Path
import shutil
import uuid

from routes import attractions, auth, accommodations, events, foods, souvenirs, safety, postcards
from routes import routes as routes_router
from fastapi.responses import RedirectResponse
from jose import JWTError, jwt
from config import settings
from limiter import limiter

# базовое логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("achinsk_app")

app = FastAPI(
    title="Ачинск туристический",
    description="Информационная система ТИЦ г. Ачинска",
    version="1.0.0"
)

# настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS.split(",") if hasattr(settings, "ALLOWED_ORIGINS") else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# подключаем лимитер к приложению
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# статика и шаблоны
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# подключение роутеров
app.include_router(auth.router, prefix="/api")
app.include_router(attractions.router)
app.include_router(accommodations.router)
app.include_router(events.router)
app.include_router(foods.router)
app.include_router(routes_router.router)
app.include_router(souvenirs.router)
app.include_router(safety.router)
app.include_router(postcards.router)

def require_admin_auth(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(url="/login", status_code=302)
    try:
        jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return RedirectResponse(url="/login?error=expired", status_code=302)

# веб-страницы
@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(request, "index.html", {"request": request})

@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html", {"request": request})

# админ-панель
@app.get("/admin", dependencies=[Depends(require_admin_auth)])
def admin_dashboard(request: Request):
    return templates.TemplateResponse(request, "admin/base_admin.html", {"request": request})

@app.get("/admin/attractions", dependencies=[Depends(require_admin_auth)])
def admin_attractions_list(request: Request):
    return templates.TemplateResponse(request, "admin/attractions_list.html", {"request": request})

@app.get("/admin/attractions/new", dependencies=[Depends(require_admin_auth)])
def admin_attractions_new(request: Request):
    return templates.TemplateResponse(request, "admin/attractions_form.html", {
        "request": request,
        "title": "Добавить достопримечательность",
        "back_url": "/admin/attractions",
        "api_path": "/attractions",
        "is_edit": False
    })

@app.get("/admin/attractions/{item_id}/edit", dependencies=[Depends(require_admin_auth)])
def admin_attractions_edit(request: Request, item_id: int):
    return templates.TemplateResponse(request, "admin/attractions_form.html", {
        "request": request,
        "title": "Редактировать достопримечательность",
        "back_url": "/admin/attractions",
        "is_edit": True,
        "item_id": item_id
    })

# маршруты
@app.get("/admin/routes", dependencies=[Depends(require_admin_auth)])
def admin_routes_list(request: Request):
    return templates.TemplateResponse(request, "admin/routes_list.html", {"request": request})

@app.get("/admin/routes/new", dependencies=[Depends(require_admin_auth)])
def admin_routes_new(request: Request):
    return templates.TemplateResponse(request, "admin/routes_form.html", {
        "request": request,
        "title": "Новый маршрут",
        "back_url": "/admin/routes",
        "api_path": "/routes",
        "is_edit": False,
        "item": None
    })

@app.get("/admin/routes/{item_id}/edit", dependencies=[Depends(require_admin_auth)])
def admin_routes_edit(request: Request, item_id: int):
    return templates.TemplateResponse(request, "admin/routes_form.html", {
        "request": request,
        "title": "Редактировать маршрут",
        "back_url": "/admin/routes",
        "is_edit": True,
        "item_id": item_id
    })

# гостиницы
@app.get("/admin/hotels", dependencies=[Depends(require_admin_auth)])
def admin_hotels_list(request: Request):
    return templates.TemplateResponse(request, "admin/hotels_list.html", {"request": request})

@app.get("/admin/hotels/new", dependencies=[Depends(require_admin_auth)])
def admin_hotels_new(request: Request):
    return templates.TemplateResponse(request, "admin/hotels_form.html", {
        "request": request,
        "title": "Новая гостиница",
        "back_url": "/admin/hotels",
        "is_edit": False,
        "item_id": None
    })

@app.get("/admin/hotels/{item_id}/edit", dependencies=[Depends(require_admin_auth)])
def admin_hotels_edit(request: Request, item_id: int):
    return templates.TemplateResponse(request, "admin/hotels_form.html", {
        "request": request,
        "title": "Редактировать гостиницу",
        "back_url": "/admin/hotels",
        "is_edit": True,
        "item_id": item_id
    })

# рестораны
@app.get("/admin/foods", dependencies=[Depends(require_admin_auth)])
def admin_food_list(request: Request):
    return templates.TemplateResponse(request, "admin/foods_list.html", {"request": request})

@app.get("/admin/foods/new", dependencies=[Depends(require_admin_auth)])
def admin_food_new(request: Request):
    return templates.TemplateResponse(request, "admin/foods_form.html", {
        "request": request,
        "title": "Новое заведение",
        "back_url": "/admin/food",
        "is_edit": False,
        "item_id": None
    })

@app.get("/admin/foods/{item_id}/edit", dependencies=[Depends(require_admin_auth)])
async def admin_food_edit(request: Request, item_id: int):
    return templates.TemplateResponse(request, "admin/foods_form.html", {
        "request": request,
        "title": "Редактировать заведение",
        "back_url": "/admin/food",
        "is_edit": True,
        "item_id": item_id
    })

# события
@app.get("/admin/events", dependencies=[Depends(require_admin_auth)])
def admin_events_list(request: Request):
    return templates.TemplateResponse(request, "admin/events_list.html", {"request": request})

@app.get("/admin/events/new", dependencies=[Depends(require_admin_auth)])
def admin_events_new(request: Request):
    return templates.TemplateResponse(request, "admin/events_form.html", {
        "request": request,
        "title": "Новое событие",
        "back_url": "/admin/events",
        "is_edit": False,
        "item_id": None
    })

@app.get("/admin/events/{item_id}/edit", dependencies=[Depends(require_admin_auth)])
def admin_events_edit(request: Request, item_id: int):
    return templates.TemplateResponse(request, "admin/events_form.html", {
        "request": request,
        "title": "Редактировать событие",
        "back_url": "/admin/events",
        "is_edit": True,
        "item_id": item_id
    })

# сувениры
@app.get("/admin/souvenirs", dependencies=[Depends(require_admin_auth)])
def admin_souvenirs_list(request: Request):
    return templates.TemplateResponse(request, "admin/souvenirs_list.html", {"request": request})

@app.get("/admin/souvenirs/new", dependencies=[Depends(require_admin_auth)])
def admin_souvenirs_new(request: Request):
    return templates.TemplateResponse(request, "admin/souvenirs_form.html", {
        "request": request,
        "title": "Новый сувенир",
        "back_url": "/admin/souvenirs",
        "is_edit": False,
        "item_id": None
    })

@app.get("/admin/souvenirs/{item_id}/edit", dependencies=[Depends(require_admin_auth)])
def admin_souvenirs_edit(request: Request, item_id: int):
    return templates.TemplateResponse(request, "admin/souvenirs_form.html", {
        "request": request,
        "title": "Редактировать сувенир",
        "back_url": "/admin/souvenirs",
        "is_edit": True,
        "item_id": item_id
    })

# безопасность
@app.get("/admin/safety", dependencies=[Depends(require_admin_auth)])
def admin_safety_list(request: Request):
    return templates.TemplateResponse(request, "admin/safety_list.html", {"request": request})

@app.get("/admin/safety/new", dependencies=[Depends(require_admin_auth)])
def admin_safety_new(request: Request):
    return templates.TemplateResponse(request, "admin/safety_form.html", {
        "request": request,
        "title": "Новая запись",
        "back_url": "/admin/safety",
        "is_edit": False,
        "item_id": None
    })

@app.get("/admin/safety/{item_id}/edit", dependencies=[Depends(require_admin_auth)])
def admin_safety_edit(request: Request, item_id: int):
    return templates.TemplateResponse(request, "admin/safety_form.html", {
        "request": request,
        "title": "Редактировать запись",
        "back_url": "/admin/safety",
        "is_edit": True,
        "item_id": item_id
    })

# открытки
@app.get("/admin/postcards", dependencies=[Depends(require_admin_auth)])
def admin_postcards_list(request: Request):
    return templates.TemplateResponse(request, "admin/postcards_list.html", {"request": request})

@app.get("/admin/postcards/new", dependencies=[Depends(require_admin_auth)])
def admin_postcards_new(request: Request):
    return templates.TemplateResponse(request, "admin/postcards_form.html", {
        "request": request,
        "title": "Новый шаблон открытки",
        "back_url": "/admin/postcards",
        "is_edit": False,
        "item_id": None
    })

@app.get("/admin/postcards/{item_id}/edit", dependencies=[Depends(require_admin_auth)])
def admin_postcards_edit(request: Request, item_id: int):
    return templates.TemplateResponse(request, "admin/postcards_form.html", {
        "request": request,
        "title": "Редактировать шаблон",
        "back_url": "/admin/postcards",
        "is_edit": True,
        "item_id": item_id
    })

# конец админки

# публичная часть
@app.get("/food")
def food_page(request: Request):
    return templates.TemplateResponse(request, "food.html", {"request": request})

@app.get("/routes")
def routes_page(request: Request):
    return templates.TemplateResponse(request, "routes.html", {"request": request})

@app.get("/attractions")
def attractions_page(request: Request): 
    return templates.TemplateResponse(request, "attractions.html", {"request": request})

@app.get("/accommodations")
def accommodations_page(request: Request): 
    return templates.TemplateResponse(request, "accommodations.html", {"request": request})

@app.get("/events")
def events_page(request: Request): 
    return templates.TemplateResponse(request, "events.html", {"request": request})

@app.get("/safety")
def safety_page(request: Request): 
    return templates.TemplateResponse(request, "safety.html", {"request": request})

@app.get("/souvenirs")
def souvenirs_page(request: Request): 
    return templates.TemplateResponse(request, "souvenirs.html", {"request": request})

@app.get("/postcards")
def postcards_page(request: Request): 
    return templates.TemplateResponse(request, "postcards.html", {"request": request})

@app.get("/map")
def map_page(request: Request):
    return templates.TemplateResponse(request, "map.html", {"request": request})

@app.get("/contacts")
def contacts_page(request: Request):
    return templates.TemplateResponse(request, "contacts.html", {"request": request})

@app.get("/inclusive")
def inclusive_page(request: Request):
    return templates.TemplateResponse(request, "inclusive.html", {"request": request})

# детальные страницы объектов
from models import Attraction, Accommodation, Food, Event, Route, SafetyObject, Souvenir
from fastapi import HTTPException

@app.get("/attractions/{item_id}")
async def attraction_detail(request: Request, item_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Attraction).where(Attraction.id == item_id))
    item = result.scalar_one_or_none()
    if not item: raise HTTPException(404, "Объект не найден")
    return templates.TemplateResponse(request, "object_detail.html", {
        "request": request, "item": item, "title": item.name, "back_url": "/attractions",
        "details": [
            ("Адрес", item.address),
            ("Рейтинг", f"{item.rating} из 5" if item.rating else None),
            ("Доступно для МГН", "Да" if item.is_accessible else None)
        ],
        "objType": "attraction",
        "description": item.description, "photo": item.photo_url
    })

@app.get("/hotels/{item_id}")
async def hotel_detail(request: Request, item_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Accommodation).where(Accommodation.id == item_id))
    item = result.scalar_one_or_none()
    if not item: raise HTTPException(404, "Гостиница не найдена")
    return templates.TemplateResponse(request, "object_detail.html", {
        "request": request, "item": item, "title": item.name, "back_url": "/accommodations",
        "details": [
            ("Адрес", item.address),
            ("Телефон", item.phone),
            ("Сайт", item.website),
            ("Цена за ночь", f"{item.price_per_night} ₽" if item.price_per_night else None),
            ("Рейтинг", f"{item.rating} из 5" if item.rating else None),
            ("Доступно для МГН", "Да" if item.is_accessible else None)
        ],
        "objType": "accommodation",
        "description": item.description, "photo": item.photo_url
    })

@app.get("/food/{item_id}")
async def food_detail(request: Request, item_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Food).where(Food.id == item_id))
    item = result.scalar_one_or_none()
    if not item: raise HTTPException(404, "Заведение не найдено")
    return templates.TemplateResponse(request, "object_detail.html", {
        "request": request, "item": item, "title": item.name, "back_url": "/food",
        "details": [
            ("Адрес", item.address),
            ("Телефон", item.phone),
            ("Кухня", item.cuisine),
            ("Средний чек", f"{item.avg_price} ₽" if item.avg_price else None),
            ("Рейтинг", f"{item.rating} из 5" if item.rating else None),
            ("Доступно для МГН", "Да" if item.is_accessible else None)
        ],
        "objType": "food",
        "description": item.description, "photo": item.photo_url
    })

@app.get("/events/{item_id}")
async def event_detail(request: Request, item_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Event).where(Event.id == item_id))
    item = result.scalar_one_or_none()
    if not item: raise HTTPException(404, "Событие не найдено")
    return templates.TemplateResponse(request, "object_detail.html", {
        "request": request, "item": item, "title": item.title, "back_url": "/events",
        "details": [
            ("Дата и время", item.event_date.strftime("%d.%m.%Y %H:%M") if item.event_date else None),
            ("Место проведения", item.location),
            ("Категория", item.category),
            ("Доступно для МГН", "Да" if item.is_accessible else None)
        ],
        "objType": "event",
        "description": item.description, "photo": item.photo_url
    })

@app.get("/routes/{item_id}")
async def route_detail(request: Request, item_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Route).where(Route.id == item_id))
    item = result.scalar_one_or_none()
    if not item: raise HTTPException(404, "Маршрут не найден")
    return templates.TemplateResponse(request, "object_detail.html", {
        "request": request, "item": item, "title": item.title, "back_url": "/routes",
        "details": [
            ("Длительность", f"{item.duration_hours} ч." if item.duration_hours else None),
            ("Сложность", item.difficulty),
            ("Транспорт", item.transport_type),
            ("Доступно для МГН", "Да" if item.is_accessible else None)
        ],
        "objType": "route",
        "description": item.description, "photo": item.photo_url
    })

@app.get("/safety/{item_id}")
async def safety_detail(request: Request, item_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SafetyObject).where(SafetyObject.id == item_id))
    item = result.scalar_one_or_none()
    if not item: raise HTTPException(404, "Объект не найден")
    return templates.TemplateResponse(request, "object_detail.html", {
        "request": request, "item": item, "title": item.name, "back_url": "/safety",
        "details": [
            ("Категория", item.category),
            ("Адрес", item.address),
            ("Телефон", item.phone)
        ],
        "objType": "safety",
        "description": None, "photo": None
    })

@app.get("/souvenirs/{item_id}")
async def souvenir_detail(request: Request, item_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Souvenir).where(Souvenir.id == item_id))
    item = result.scalar_one_or_none()
    if not item: raise HTTPException(404, "Сувенир не найден")
    return templates.TemplateResponse(request, "object_detail.html", {
        "request": request, "item": item, "title": item.name, "back_url": "/souvenirs",
        "details": [
            ("Производитель", item.producer),
            ("Цена", f"{item.price} ₽" if item.price else None),
            ("Категория", item.category),
            ("Доступно для МГН", "Да" if item.is_accessible else None)
        ],
        "objType": "souvenir",
        "description": item.description, "photo": item.photo_url
    })

# загрузка файлов
UPLOAD_DIR = Path("static/uploads/images")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}

@app.post("/api/upload/")
async def upload_file(file: UploadFile = File(...)):
    file_ext = Path(file.filename or "").suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Недопустимый формат файла")
    
    allowed_types = ["image/jpeg", "image/png", "image/webp", "image/gif"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Недопустимый формат файла. Разрешены: JPEG, PNG, WebP, GIF")
    
    file_size = 0
    for chunk in file.file:
        file_size += len(chunk)
        if file_size > 5 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Файл слишком большой (макс. 5MB)")
    
    file_extension = file.filename.split(".")[-1]
    unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
    file_path = UPLOAD_DIR / unique_filename
    
    with file_path.open("wb") as buffer:
        file.file.seek(0)
        shutil.copyfileobj(file.file, buffer)
    
    file_url = f"/static/uploads/images/{unique_filename}"
    return {"file_url": file_url, "filename": unique_filename}

# единый обработчик ошибок
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    titles = {
        400: "Некорректный запрос",
        401: "Требуется авторизация",
        403: "Доступ запрещен",
        404: "Страница не найдена",
        422: "Ошибка валидации данных",
        500: "Внутренняя ошибка сервера"
    }
    return templates.TemplateResponse(
        request, "error.html",
        {
            "request": request,
            "status_code": exc.status_code,
            "title": titles.get(exc.status_code, "Произошла ошибка"),
            "message": exc.detail if isinstance(exc.detail, str) else "Неизвестная ошибка"
        },
        status_code=exc.status_code
    )