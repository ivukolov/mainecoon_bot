from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request, APIRouter
from fastapi.responses import RedirectResponse
from sqladmin import Admin

from config import settings
from core.models import BaseModel
from web.admin import setup_admin_panel


class AppSingleton:
    _instance = None
    _app = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AppSingleton, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        if self._app is None:
            self._app = self._make_app()

    def _make_app(self) -> FastAPI:
        return FastAPI(
            title=settings.PROJECT_NAME,
            debug=settings.DEBUG
        )

    @property
    def app(self) -> FastAPI:
        """Получить экземпляр приложения"""
        if self._app is None:
            raise RuntimeError("Приложение не инициализировано")
        return self._app


app_singleton = AppSingleton()

def get_app() -> FastAPI:
    return app_singleton.app

async def run_fastapi():
    """Запуск FastAPI сервера"""
    app = get_app()
    setup_admin_panel(app)
    config = uvicorn.Config(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info",
    )
    server = uvicorn.Server(config)
    await server.serve()