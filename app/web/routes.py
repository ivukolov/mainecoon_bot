from fastapi.responses import RedirectResponse

from web.app import get_app

app = get_app()


@app.get("/")
async def redirect_to_admin_panel():
    return RedirectResponse('/admin', status_code=308)