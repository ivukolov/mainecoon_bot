import importlib
from typing import Dict, Any

from app.config import settings


def import_string(dotted_path: str):
    """Импорт класса/функции по строковому пути"""
    module_path, class_name = dotted_path.rsplit('.', 1)
    module = importlib.import_module(module_path)
    return getattr(module, class_name)


def make_callable(obj, kwargs):
    """Вызов объекта с переданными аргументами"""
    obj = import_string(obj)
    return obj(**kwargs)

def get_callable_from_settings(dict_key: str) -> dict:
    return {
        name: make_callable(
            value, value.get('kwargs') if isinstance(value, dict) else None
        ) for name, value in settings.LOGGING.get(
            dict_key, {}
        ).items()
    }