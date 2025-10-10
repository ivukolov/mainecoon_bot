from contextlib import asynccontextmanager
from logging import getLogger

from fastapi import FastAPI, Request, APIRouter
from fastapi.responses import RedirectResponse
from sqladmin import Admin
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from utils.bot_utils import get_or_create_admin_user
from config import settings
from core.models import BaseModel
from database.db import engine, get_db_session_directly
from web.admin import setup_admin_panel
from web.routes import router
from web.midleware import DatabaseMiddleware

logger = getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    session = await get_db_session_directly()
    await get_or_create_admin_user(session)
    yield
    session.close()

app = FastAPI(
    title=settings.PROJECT_NAME,
    debug=settings.DEBUG,
    engine=engine,
    lifespan=lifespan,
    middleware=[
        Middleware(
            DatabaseMiddleware
        ),
        Middleware(
            CORSMiddleware, allow_origins=[
                "http://localhost",
                "http://127.0.0.1",
                f"http://{settings.DOMAIN_NAME}",
                f"https://{settings.DOMAIN_NAME}",
            ],
        allow_credentials = True,
        allow_methods = ["*"],
        allow_headers = ["*"],
        ),
    ]
)
setup_admin_panel(app)
app.include_router(router)

async def run_fastapi():
    logger.info("Запуск админ панели.")
    import uvicorn
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
    )
    server = uvicorn.Server(config)
    await server.serve()