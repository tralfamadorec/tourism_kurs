from fastapi import FastAPI

app = FastAPI(
    title="Ачинск туристический",
    description="Информационная система ТИЦ г. Ачинска",
    version="0.1.0"
)

@app.get("/")
def root():
    return {"status": "ok", "message": "Сервер запущен"}