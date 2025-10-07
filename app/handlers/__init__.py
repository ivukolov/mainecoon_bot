from handlers.commands import commands_router
from handlers.main_menu import main_menu_router
from handlers.admin import admin_router
from handlers.blog import blog_router
from handlers.partners import partners_router
from handlers.ads import ads_router
from handlers.channel_posts import channel_listener
from handlers.users import users_router
from handlers.about import about_router
from handlers import polls_router


routers = (
    users_router,
    channel_listener,
    admin_router,
    commands_router,
    main_menu_router,
    blog_router,
    partners_router,
    ads_router,
    polls_router,
    about_router,
)