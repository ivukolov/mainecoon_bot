import uuid

def generate_uuid_from_str(name: str) -> str:
    name_space = uuid.NAMESPACE_OID
    try:
        username = str(uuid.uuid5(name_space, str(name)))
    except ValueError:
        raise ValueError('Ошибка преобразования строки при формирование UUID из id пользователя')
    return username