from fastapi import FastAPI
from routes import attractions
from routes import auth
from routes import accomodations

app = FastAPI(
    title="Ачинск туристический",
    description="Информационная система ТИЦ г. Ачинска",
    version="0.1.0"
)

app.include_router(attractions.router)
app.include_router(auth.router)
app.include_router(accomodations.router)

@app.get("/")
def root():
    return {"status": "ok", "message": "Сервер запущен"}