from sqladmin import Admin
from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse, Response

from database.db import engine
from database.users.models import User
from web.authentication import AdminAuth
from web.views import UserAdmin, TagAdmin, CategoryAdmin, PostAdmin, TelegramSessionAdmin

from config import settings


class CustomAdmin(Admin):
    async def login(self, request: Request) -> Response:
        assert self.authentication_backend is not None

        context = {}
        if request.method == "GET":
            return await self.templates.TemplateResponse(request, "sqladmin/login.html")

        ok, context = await self.authentication_backend.login(request)
        if not ok:
            return await self.templates.TemplateResponse(
                request, "sqladmin/login.html", context, status_code=400
            )

        return RedirectResponse(request.url_for("admin:index"), status_code=302)


def setup_admin_panel(app):
    authentication_backend = AdminAuth(secret_key=settings.FAST_API_SECRET_KEY)
    admin = CustomAdmin(
        app=app,
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
    admin.add_view(TelegramSessionAdmin)
    return admin