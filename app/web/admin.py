from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqladmin import ModelView, Admin

from database.db import get_db_session, engine
from database.users.models import User
from app.web.views import UserAdmin, TagAdmin, CategoryAdmin, PostAdmin

def setup_admin_panel(app):
    admin = Admin(
        app=app,  # Will be set in main.py
        engine=engine,
        # authentication_backend=authentication_backend,
        title="Blog Admin",
        base_url="/admin",
        # templates_dir="templates/admin",
    )

    # Register views
    admin.add_view(UserAdmin)
    admin.add_view(TagAdmin)
    admin.add_view(CategoryAdmin)
    admin.add_view(PostAdmin)
    return admin