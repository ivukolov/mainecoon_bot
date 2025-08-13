from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart

from keyboards.main_menu import blog_categories_kb, main_menu_kb

command_start_router = Router()

@command_start_router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "Привет! Я — бот канала «Мейн-куны в Воронеже».\n\n"
        "📌 Выбери раздел:",
        reply_markup=main_menu_kb()
    )

@command_start_router.message(F.text == "🐾 Блог (рубрики)")
async def blog_menu(message: Message):
    await message.answer("Выберите рубрику блога:", reply_markup=blog_categories_kb())