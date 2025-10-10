from sqladmin import Admin

from database.db import engine
from database.users.models import User
from web.authentication import AdminAuth
from web.views import UserAdmin, TagAdmin, CategoryAdmin, PostAdmin

from config import settings


def setup_admin_panel(app):
    authentication_backend = AdminAuth(secret_key=settings.FAST_API_SECRET_KEY)
    admin = Admin(
        app=app,  # Will be set in main.py
        engine=engine,
        authentication_backend=authentication_backend,
        title=settings.PROJECT_NAME,
        base_url="/admin",
        # templates_dir="templates/admin",
    )

    # Register views
    admin.add_view(UserAdmin)
    admin.add_view(TagAdmin)
    admin.add_view(CategoryAdmin)
    admin.add_view(PostAdmin)
    return admin