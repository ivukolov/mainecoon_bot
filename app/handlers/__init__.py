from handlers.commands import commands_router
from handlers.main_menu import main_menu_router
from handlers.admin import admin_router
from handlers.blog import blog_router
from handlers.partners import partners_router
from handlers.ads.handler import ads_router
from handlers.channel_posts import channel_listener
from handlers.users import users_router
from handlers.about import about_router
from handlers.interactives import interactives_router
from handlers.background import background_router


routers = (
    background_router,
    users_router,
    channel_listener,
    admin_router,
    commands_router,
    main_menu_router,
    blog_router,
    partners_router,
    ads_router,
    interactives_router,
    about_router,
)