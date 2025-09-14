from handlers.start import command_start_router
from handlers.admin import admin_router


routers = (
    command_start_router,
    admin_router
)