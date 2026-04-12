from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from routes import attractions, auth, accommodations, events, restaurants
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

# настройка раздачи статики
if not os.path.exists("static"):
    os.makedirs("static")

app.mount("/static", StaticFiles(directory="static"), name="static")

# подключение роутеров
app.include_router(attractions.router)
app.include_router(auth.router)
app.include_router(accommodations.router)
app.include_router(events.router)
app.include_router(routes_router.router)

@app.get("/")
def root():
    return {"status": "ok", "message": "Backend API is ready for Frontend integration"}