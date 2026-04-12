from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os

from routes import attractions, auth, accommodations, events, restaurants, souvenirs, safety, postcards
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
app.include_router(restaurants.router)
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
        "api_path": "/attractions",
        "is_edit": True,
        "item": None
    })

# заглушки для остальных страниц 
@app.get("/attractions")
def attractions_page(request: Request): return templates.TemplateResponse(request, "attractions.html", {"request": request})
@app.get("/routes")
def routes_page(request: Request): return templates.TemplateResponse(request, "routes.html", {"request": request})
@app.get("/hotels")
def hotels_page(request: Request): return templates.TemplateResponse(request, "hotels.html", {"request": request})
@app.get("/food")
def food_page(request: Request): return templates.TemplateResponse(request, "food.html", {"request": request})
@app.get("/events")
def events_page(request: Request): return templates.TemplateResponse(request, "events.html", {"request": request})
@app.get("/safety")
def safety_page(request: Request): return templates.TemplateResponse(request, "safety.html", {"request": request})
@app.get("/souvenirs")
def souvenirs_page(request: Request): return templates.TemplateResponse(request, "souvenirs.html", {"request": request})
@app.get("/postcards")
def postcards_page(request: Request): return templates.TemplateResponse(request, "postcards.html", {"request": request})