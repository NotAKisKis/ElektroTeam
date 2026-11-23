from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import init_db


@asynccontextmanager
async def lifespan(app):
    print("Приложение запускается")
    init_db()
    yield
    print("Приложение останавливается")

app = FastAPI(lifespan=lifespan)

@app.get("/health")
def health():
    return {"status": "ok"}