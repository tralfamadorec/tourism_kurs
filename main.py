from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import httpx
from fastapi import HTTPException

from routes import attractions, auth, accommodations, events, foods, souvenirs, safety, postcards
from routes import routes as routes_router

app = FastAPI(
    title="Ачинск туристический",
    description="Информационная система ТИЦ г. Ачинска",
    version="1.0.0"
)

# настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# веб-страницы
@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(request, "index.html", {"request": request})

@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html", {"request": request})

# админ-панель
@app.get("/admin")
def admin_dashboard(request: Request):
    return templates.TemplateResponse(request, "admin/base_admin.html", {"request": request})

# достопримечательности
@app.get("/admin/attractions")
def admin_attractions_list(request: Request):
    return templates.TemplateResponse(request, "admin/attractions_list.html", {"request": request})

@app.get("/admin/attractions/new")
def admin_attractions_new(request: Request):
    return templates.TemplateResponse(request, "admin/attractions_form.html", {
        "request": request,
        "title": "Добавить достопримечательность",
        "back_url": "/admin/attractions",
        "api_path": "/attractions",
        "is_edit": False
    })

@app.get("/admin/attractions/{item_id}/edit")
def admin_attractions_edit(request: Request, item_id: int):
    return templates.TemplateResponse(request, "admin/attractions_form.html", {
        "request": request,
        "title": "Редактировать достопримечательность",
        "back_url": "/admin/attractions",
        "is_edit": True,
        "item_id": item_id
    })

# маршруты
@app.get("/admin/routes")
def admin_routes_list(request: Request):
    return templates.TemplateResponse(request, "admin/routes_list.html", {"request": request})

@app.get("/admin/routes/new")
def admin_routes_new(request: Request):
    return templates.TemplateResponse(request, "admin/routes_form.html", {
        "request": request,
        "title": "Новый маршрут",
        "back_url": "/admin/routes",
        "api_path": "/routes",
        "is_edit": False,
        "item": None
    })

@app.get("/admin/routes/{item_id}/edit")
def admin_routes_edit(request: Request, item_id: int):
    return templates.TemplateResponse(request, "admin/routes_form.html", {
        "request": request,
        "title": "Редактировать маршрут",
        "back_url": "/admin/routes",
        "is_edit": True,
        "item_id": item_id
    })

# гостиницы
@app.get("/admin/hotels")
def admin_hotels_list(request: Request):
    return templates.TemplateResponse(request, "admin/hotels_list.html", {"request": request})

@app.get("/admin/hotels/new")
def admin_hotels_new(request: Request):
    return templates.TemplateResponse(request, "admin/hotels_form.html", {
        "request": request,
        "title": "Новая гостиница",
        "back_url": "/admin/hotels",
        "is_edit": False,
        "item_id": None
    })

@app.get("/admin/hotels/{item_id}/edit")
def admin_hotels_edit(request: Request, item_id: int):
    return templates.TemplateResponse(request, "admin/hotels_form.html", {
        "request": request,
        "title": "Редактировать гостиницу",
        "back_url": "/admin/hotels",
        "is_edit": True,
        "item_id": item_id
    })

# рестораны
@app.get("/admin/food")
def admin_food_list(request: Request):
    return templates.TemplateResponse(request, "admin/foods_list.html", {"request": request})

@app.get("/admin/food/new")
def admin_food_new(request: Request):
    return templates.TemplateResponse(request, "admin/foods_form.html", {
        "request": request,
        "title": "Новое заведение",
        "back_url": "/admin/food",
        "is_edit": False,
        "item_id": None
    })

@app.get("/admin/food/{item_id}/edit")
def admin_food_edit(request: Request, item_id: int):
    return templates.TemplateResponse(request, "admin/foods_form.html", {
        "request": request,
        "title": "Редактировать заведение",
        "back_url": "/admin/food",
        "is_edit": True,
        "item_id": item_id
    })

# события
@app.get("/admin/events")
def admin_events_list(request: Request):
    return templates.TemplateResponse(request, "admin/events_list.html", {"request": request})

@app.get("/admin/events/new")
def admin_events_new(request: Request):
    return templates.TemplateResponse(request, "admin/events_form.html", {
        "request": request,
        "title": "Новое событие",
        "back_url": "/admin/events",
        "is_edit": False,
        "item_id": None
    })

@app.get("/admin/events/{item_id}/edit")
def admin_events_edit(request: Request, item_id: int):
    return templates.TemplateResponse(request, "admin/events_form.html", {
        "request": request,
        "title": "Редактировать событие",
        "back_url": "/admin/events",
        "is_edit": True,
        "item_id": item_id
    })

# сувениры
@app.get("/admin/souvenirs")
def admin_souvenirs_list(request: Request):
    return templates.TemplateResponse(request, "admin/souvenirs_list.html", {"request": request})

@app.get("/admin/souvenirs/new")
def admin_souvenirs_new(request: Request):
    return templates.TemplateResponse(request, "admin/souvenirs_form.html", {
        "request": request,
        "title": "Новый сувенир",
        "back_url": "/admin/souvenirs",
        "is_edit": False,
        "item_id": None
    })

@app.get("/admin/souvenirs/{item_id}/edit")
def admin_souvenirs_edit(request: Request, item_id: int):
    return templates.TemplateResponse(request, "admin/souvenirs_form.html", {
        "request": request,
        "title": "Редактировать сувенир",
        "back_url": "/admin/souvenirs",
        "is_edit": True,
        "item_id": item_id
    })

# безопасность
@app.get("/admin/safety")
def admin_safety_list(request: Request):
    return templates.TemplateResponse(request, "admin/safety_list.html", {"request": request})

@app.get("/admin/safety/new")
def admin_safety_new(request: Request):
    return templates.TemplateResponse(request, "admin/safety_form.html", {
        "request": request,
        "title": "Новая запись",
        "back_url": "/admin/safety",
        "is_edit": False,
        "item_id": None
    })

@app.get("/admin/safety/{item_id}/edit")
def admin_safety_edit(request: Request, item_id: int):
    return templates.TemplateResponse(request, "admin/safety_form.html", {
        "request": request,
        "title": "Редактировать запись",
        "back_url": "/admin/safety",
        "is_edit": True,
        "item_id": item_id
    })

# открытки
@app.get("/admin/postcards")
def admin_postcards_list(request: Request):
    return templates.TemplateResponse(request, "admin/postcards_list.html", {"request": request})

@app.get("/admin/postcards/new")
def admin_postcards_new(request: Request):
    return templates.TemplateResponse(request, "admin/postcards_form.html", {
        "request": request,
        "title": "Новый шаблон открытки",
        "back_url": "/admin/postcards",
        "is_edit": False,
        "item_id": None
    })

@app.get("/admin/postcards/{item_id}/edit")
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