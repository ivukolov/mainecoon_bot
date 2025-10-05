from fastapi import APIRouter
from fastapi.responses import RedirectResponse

router = APIRouter()

# @router.get("/")
# async def redirect_to_admin_panel():
#     return RedirectResponse('/admin', status_code=308)