import pathlib
from io import BytesIO
from logging import getLogger
from typing import Any, BinaryIO, Union, Optional
import os

import aiofiles
import aiofiles.os as  async_os

from config import settings


logger = getLogger(__name__)


def get_images_paths(tg_user_id: str)-> tuple[str, str]:
   """
   Формирует путь из id пользователя для url и путь для сохранения файла
   Returns:
       Tuple(local_path, global_path)
   """
   local_path = os.path.join(settings.IMAGES, tg_user_id)
   global_path = os.path.join(settings.IMAGES_ROOT, tg_user_id)
   return local_path, global_path

async def save_file(file_path: str, file_bytes: Union[bytes, BytesIO, BinaryIO]) -> Optional[str]:
    """Асинхронный метод сохранения файла
    Arguments:
        file_path: Место сохранения файла
        file_bytes: Байты для сохранения файла
    Returns:
        file_path: str | None
        """
    try:
        if isinstance(file_bytes, (BytesIO, BinaryIO)):
            file_bytes = file_bytes.getvalue()
        directory = os.path.dirname(file_path)
        await async_os.makedirs(directory, exist_ok=True)
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file_bytes)
        return file_path
    except FileNotFoundError as e:
      logger.error(
         "Нужно создать директорию перед записью: %s", e
      )

    except PermissionError as e:
      logger.error(
         "Нет прав на запись в директорию: %s",  e
                   )

    except IsADirectoryError as e:
      logger.error(
         "Передан путь к директории вместо файла: %s", e
      )

    except OSError as e:
      logger.error("Ошибка записи на диск: %s", e)

    except Exception as e:
      logger.error("Неожиданное исключение записи данных: %s", e)
      # Любые другие непредвиденные ошибки
    return None