from datetime import datetime
from enum import StrEnum
from typing import Optional, List

import sqlalchemy as sa
import sqlalchemy.orm as orm

from core.models import BaseModel
from database.users.models import User
from config import settings


class MediaType(StrEnum):
    PHOTO = "photo"
    VIDEO = "video"
    DOCUMENT = "document"


# class PostTag(BaseModel):
#     __tablename__ = 'post_tags'
#
#     post_id = Column(Integer, ForeignKey('posts.id'), primary_key=True)
#     tag_id = Column(Integer, ForeignKey('tags.id'), primary_key=True)
#
#     # Опциональные связи для удобства
#     post = relationship('Post', back_populates='tags')
#     tag = relationship('Tag', back_populates='posts')
post_tags = sa.Table(
    'post_tags', BaseModel.metadata,
    sa.Column('post_id', sa.Integer, sa.ForeignKey('posts.id'), primary_key=True),
    sa.Column('tag_id', sa.Integer, sa.ForeignKey('tags.id'), primary_key=True),
)

# user_invites = sa.Table(
#     'user_invites', BaseModel.metadata,
#     sa.Column('user_invited', sa.Integer, sa.ForeignKey('users.id'), primary_key=True),
#     sa.Column('user_inviting', sa.Integer, sa.ForeignKey('users.id'), primary_key=True),
# )

class Tag(BaseModel):
    __tablename__ = "tags"

    name: orm.Mapped[str] = orm.mapped_column(
        sa.String(settings.TAG_NAME_LENGTH),
        nullable=False,
        unique=True,
        info={
        "verbose_name": "Название тэга",
        "help_text": "Уникальный тэг для постов"
        }
    )
    emoji: orm.Mapped[str] = orm.mapped_column(
        sa.Unicode(settings.TAG_EMOJI_LENGTH),
        nullable=True,
        unique=False,
        info={
            "verbose_name": "Emoji тэга",
            "help_text": "Emoji в Unicode для добавления к тэгам"
        }
    )
    posts: orm.Mapped[List["Post"]] = orm.relationship(
        "Post",
        secondary=post_tags,
        back_populates="tags",
        lazy="selectin"
    )


    def __str__(self):
        return self.name

    @classmethod
    async def get_tag(cls,session,  tag_name) -> List['Post',]:
        query = sa.select(cls).filter(cls.name.like(f"%{tag_name}%"))
        rsult =  await session.execute(query)
        return rsult.scalars().first()



class Category(BaseModel):
    __tablename__ = "categories"

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    name: orm.Mapped[str] = orm.mapped_column(sa.String(50), unique=True)
    slug: orm.Mapped[str] = orm.mapped_column(sa.String(50), unique=True)

    # Отношение один-ко-многим к постам
    posts: orm.Mapped[List["Post"]] = orm.relationship(
        "Post",
        back_populates="category",
        lazy="selectin"
    )

    def __str__(self):
        return self.name

class Post(BaseModel):
    __tablename__ = "posts"

    id: orm.Mapped[int] = orm.mapped_column(
        sa.Integer, primary_key=True, nullable=False, comment='id поста из telegram', unique=True
    )
    date: orm.Mapped[datetime] = orm.mapped_column(sa.DateTime(timezone=True), comment='Дата создания поста.')
    edit_date: orm.Mapped[datetime] = orm.mapped_column(sa.DateTime, nullable=True, comment='Дата Изменения поста.')
    title: orm.Mapped[str] = orm.mapped_column(sa.String(settings.POST_TITLE_LENGTH), nullable=False, comment='Название поста.' )
    message: orm.Mapped[str] = orm.mapped_column(sa.Text, nullable=False, comment='Сообщение из поста')
    author_id: orm.Mapped[int] = orm.mapped_column(sa.ForeignKey("users.id", comment='Автор поста'), nullable=True)
    category_id: orm.Mapped[int] = orm.mapped_column(sa.ForeignKey("categories.id"), comment='Категория поста', nullable=True)
    views: orm.Mapped[int] = orm.mapped_column(sa.Integer, nullable=True, comment="Количество просмотров")
    forwards: orm.Mapped[int] = orm.mapped_column(sa.Integer, nullable=True, comment="Количество пересылок")
    # media: Mapped[str] = mapped_column(Text, nullable=True, comment='Фото из поста')

    # Один к одному.
    author: orm.Mapped[User] = orm.relationship("User", back_populates="posts")
    category: orm.Mapped[Category] = orm.relationship("Category", back_populates="posts")

    tags: orm.Mapped[List["Tag"]] = orm.relationship(
        "Tag",
        secondary=post_tags,
        back_populates="posts",
        lazy = "selectin"
    )

    def __str__(self):
        return self.title

    @classmethod
    async def get_last_post(cls, session) -> 'Post':
        query = sa.select(cls).order_by(cls.date.desc()).limit(1)
        result = await session.execute(query)
        return result.scalar_one_or_none()




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

