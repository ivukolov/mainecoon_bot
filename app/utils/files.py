from io import BytesIO
from pathlib import Path
from aiopath import AsyncPath
from logging import getLogger
from typing import Any, BinaryIO, Union, Optional, Collection, Dict, List, Tuple
import os

import aiofiles
import aiofiles.os as async_os

from config import settings

logger = getLogger(__name__)


def get_images_paths(directory: str | Path) -> tuple[str, Path]:
    """
    Формирует локальный  и  глобальный путь для сохранения файла - на основе id пользователя
    Returns:
        Tuple(local_path(posix:str), global_path: Path)
    """
    local_path = (settings.IMAGES_DIR / directory).as_posix()
    global_path = settings.IMAGES_ROOT / directory
    return local_path, global_path


async def save_file(file_path: str | Path, file_bytes: Union[bytes, BytesIO, BinaryIO]) -> str:
    """Асинхронный метод сохранения файла
    Arguments:
        file_path: Место сохранения файла
        file_bytes: Байты для сохранения файла
    Returns:
        file_path: str | None
    Exceptions:
        Выбрасывает исключение если не получается сохранить файл.
        """
    try:
        if isinstance(file_bytes, (BytesIO, BinaryIO)):
            file_bytes = file_bytes.getvalue()
        directory = AsyncPath(file_path).parent
        await AsyncPath(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f'Сохраняю файл {file_path}')
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file_bytes)
        return file_path
    except FileNotFoundError as e:
        logger.error(
            "Нужно создать директорию перед записью: %s", e
        )
        raise

    except PermissionError as e:
        logger.error(
            "Нет прав на запись в директорию: %s", e
        )
        raise

    except IsADirectoryError as e:
        logger.error(
            "Передан путь к директории вместо файла: %s", e
        )
        raise

    except OSError as e:
        logger.error("Ошибка записи на диск: %s", e)
        raise

    except Exception as e:
        logger.error("Неожиданное исключение записи данных: %s", e)
        # Любые другие непредвиденные ошибки
        raise


async def atomic_save_files(
        files: Dict[str, Union[bytes, BytesIO, BinaryIO]], mode: str = 'w'
) -> bool:
    """
    Атомарное сохранение с использованием asynctempfile
    Arguments:
        files: dict Принимает словарь с аргументами: Ключ: полный путь к файлу, Значение: байты для сохранения

    """
    if not files:
        return False
    saved_files: List[AsyncPath, ...] | List = [] # Стэк сохранённых файлов
    try:
        for file_path, content in files.items():
            file_path = AsyncPath(file_path)
            await save_file(file_path, content)
            saved_files.append(file_path)
        return True
    except Exception as e:
        logger.error("Ошибка при атомарном сохранении файлов: %s", e)
        try:
            if saved_files:
                logger.debug("Удаляем файлы: %s", saved_files)
                for file_path in saved_files:
                    if file_path.exists():
                        file_path.unlink()
                        logger.debug("Файл: %s удалён.", file_path)
        except Exception as e:
            logger.warning('Ошибка очищения файлов в рамках атомарной операции %s', e)
        return False