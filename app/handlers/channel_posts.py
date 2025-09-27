import typing as t

from aiogram import Router, types

channel_listener = Router()



@channel_listener.channel_post()
async def handle_channel_post(channel_post: types.Message):
    """Получение базовой информации о сообщении в канале"""

    # Информация о канале (чате)
    channel_info = (
        f'channel_id: {channel_post.chat.id},\n'
        f'channel_title: {channel_post.chat.title},\n'
        f'channel_username: {channel_post.chat.username},\n'
        f'message_id: {channel_post.message_id},\n'
        f'date: {channel_post.date},\n'
        f'text: {channel_post.text},\n'
        f'caption: {channel_post.caption}\n'
    )

    print("Информация о канале:")
    for key, value in channel_info.items():
        print(f"{key}: {value}")

    # Попытка получить автора (если есть)
    if channel_post.author_signature:
        print(f"Подпись автора: {channel_post.author_signature}")

    if channel_post.sender_chat:
        print(f"Отправитель (чат): {channel_post.sender_chat.title}")
    await channel_post.bot.send_message(chat_id=1382354642, text=channel_info)


@channel_listener.edited_channel_post()
async def handle_edited_channel_post(edited_channel_post: types.Message):
    """
    Обработчик для отредактированных сообщений в канале
    """
    print(f"Сообщение отредактировано: {edited_channel_post.text}")
