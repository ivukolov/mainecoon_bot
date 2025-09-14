from datetime import datetime
from enum import StrEnum
from typing import Optional, List

from sqlalchemy import String, Unicode, Integer, DateTime, Text, LargeBinary, BigInteger, Boolean, Float, Table, Column, \
    ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models import BaseModel
from database.users.models import User
from config import settings


class MediaType(StrEnum):
    PHOTO = "photo"
    VIDEO = "video"
    DOCUMENT = "document"


post_tag_association = Table(
    'post_tag_association',
    BaseModel.metadata,
    Column('post_id', Integer, ForeignKey('posts.post_id', ondelete='CASCADE'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True),
)

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
    posts = relationship("Post", secondary=post_tag_association, back_populates="tags")

    def __str__(self):
        return self.name


class Category(BaseModel):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    slug: Mapped[str] = mapped_column(String(50), unique=True)

    # Отношение один-ко-многим к постам
    posts: Mapped[List["Post"]] = relationship(
        "Post",
        back_populates="category",
        lazy="selectin"
    )

    def __str__(self):
        return self.name

class Post(BaseModel):
    __tablename__ = "posts"

    post_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, nullable=False, comment='id поста из telegram'
    )
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), comment='Дата создания поста.')
    edit_dat: Mapped[datetime] = mapped_column(DateTime, nullable=True, comment='Дата Изменения поста.')
    title: Mapped[str] = mapped_column(String(200), nullable=False, comment='Название поста.' )
    message: Mapped[str] = mapped_column(Text, nullable=False, comment='Сообщение из поста')
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id", comment='Автор поста'))
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), comment='Категория поста')
    # photos: Mapped[str] = mapped_column(Text, nullable=True, comment='Фото из поста')

    # Один к одному.
    author: Mapped[User] = relationship("User", back_populates="posts")
    category: Mapped[Category] = relationship("Category", back_populates="posts")

    # многие ко многим.
    tags: Mapped[List['Tag']] = relationship(
        secondary=post_tag_association,
        back_populates='posts',
        cascade='all, delete',
        lazy='selectin',
    )

    def __str__(self):
        return self.title


# class MediaBase:
#     """Базовый миксин для всех медиа-типов"""
#
#     id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
#     access_hash: Mapped[int] = mapped_column(BigInteger, comment='Ключ доступа к файлу.')
#     file_reference: Mapped[bytes] = mapped_column(LargeBinary, nullable=False,
#                                                   comment="Байтовая строка для обновления access_hash")
#     date: Mapped[datetime] = mapped_column(DateTime(timezone=True),
#                                            comment='Дата и время загрузки файла на сервер Telegram')
#     dc_id: Mapped[int] = mapped_column(Integer)
#     filename: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
#     file_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment="Размер файла в байтах.")
#     mime_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, comment="MIME-тип файла, который определяет его формат и тип содержимого.")
#     media_type: Mapped[MediaType] = mapped_column(String(20), default=MediaType.PHOTO,
#                                                   comment="Таблица для классификации медиа-файлов")
#
#
# class Photo(BaseModel, MediaBase):
#     __tablename__ = "photos"
#
#     photo_id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, comment="Уникальный идентификатор файла на серверах Telegram. ")
#     width: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
#     height: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
#     color_mode: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
#     has_alpha: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
#     exif_data: Mapped[Optional[bytes]] = mapped_column(LargeBinary, nullable=True)
#
#
#     def __repr__(self) -> str:
#         return f"Photo(id={self.id}, filename={self.filename!r})"
#
#
# class Video(BaseModel, MediaBase):
#     __tablename__ = 'videos'
#
#     duration: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
#     width: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
#     height: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
#     fps: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
#     bitrate: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
#     codec: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
#     has_audio: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
#     thumbnail_path: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
#
#
# class GIF(BaseModel, MediaBase):
#     __tablename__ = 'gifs'
#
#     width: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
#     height: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
#     duration: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
#     frame_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
#     loop_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
#     is_animated: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)

