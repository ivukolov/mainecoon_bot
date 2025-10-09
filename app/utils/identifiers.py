import uuid

def generate_username_from_id(tg_user_id: int) -> str:
    name_space = uuid.NAMESPACE_OID
    try:
        username = str(uuid.uuid5(name_space, str(tg_user_id)))
    except ValueError:
        raise ValueError('Ошибка преобразования строки при формирование UUID из id пользователя')
    return username