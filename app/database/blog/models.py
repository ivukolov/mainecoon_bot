from sqlalchemy import String, Unicode
from sqlalchemy.orm import Mapped, mapped_column

from core.models import BaseModel
from config import settings

class Tag(BaseModel):
    __tablename__ = "tags"

    name: Mapped[str] = mapped_column(
        String(settings.TAG_NAME_LENGTH),
        nullable=False,
        unique=True,
        info={
        "verbose_name": "Название тэга",
        "help_text": "Уникальный тэг для постов"
        }
    )
    emoji: Mapped[str] = mapped_column(
        Unicode(settings.TAG_EMOJI_LENGTH),
        nullable=True,
        unique=False,
        info={
            "verbose_name": "Emoji тэга",
            "help_text": "Emoji в Unicode для добавления к тэгам"
        }
    )

