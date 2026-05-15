from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from database import init_db
import routers.auth as auth
import routers.devices as devices
import routers.scenarios as scenarios
import routers.logs as logs

# Lifespan-обработчик: старт и остановка
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Действия при старте
    init_db()
    # При необходимости здесь можно создать пул соединений, фоновые задачи и т.д.
    yield
    # Действия при завершении (если нужны)
    # Например, закрыть соединения с БД

app = FastAPI(
    title="Умный дом",
    lifespan=lifespan  # передаём lifespan вместо @app.on_event()
)

# Шаблоны и статика остаются без изменений
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Подключаем роутеры
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(devices.router, prefix="/devices", tags=["devices"])
app.include_router(scenarios.router, prefix="/scenarios", tags=["scenarios"])
app.include_router(logs.router, prefix="/logs", tags=["logs"])

@app.get("/")
async def root():
    return {"message": "Добро пожаловать в Умный дом"}