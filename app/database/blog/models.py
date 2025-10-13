from datetime import datetime, date
from decimal import Decimal
from enum import StrEnum, Enum
import typing as t

import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.dialects.postgresql import JSONB

from core.models import BaseModel
from config import settings

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


class Tag(BaseModel):
    __tablename__ = "tags"

    name: orm.Mapped[str] = orm.mapped_column(
        sa.String(settings.TAG_NAME_LENGTH),
        nullable=False,
        index=True,
        unique=True,
        comment='Имя'
    )
    emoji: orm.Mapped[str] = orm.mapped_column(
        sa.Unicode(settings.TAG_EMOJI_LENGTH),
        nullable=True,
        unique=False,
    )
    posts: orm.Mapped[t.List["Post"]] = orm.relationship(
        "Post",
        secondary=post_tags,
        back_populates="tags",
        lazy="selectin",
    )

    def __str__(self):
        return self.name

    @classmethod
    async def get_tag(cls, session, tag_name) -> t.List['Post',]:
        query = sa.select(cls).filter(cls.name.like(f"%{tag_name}%"))
        rsult = await session.execute(query)
        return rsult.scalars().first()

    @classmethod
    async def bulk_get_or_create_tags(cls, session, tags: t.Set[str]) -> t.Dict[str, 'Tag']:
        if not tags:
            return {}

        existing_tags_stmt = sa.select(cls).where(cls.name.in_(tags))
        existing_tags_result = await session.execute(existing_tags_stmt)
        existing_tags = {tag.name: tag for tag in existing_tags_result.scalars()}
        tags_to_create = tags - set(existing_tags.keys())
        if tags_to_create:
            new_tags = []
            for tag_name in tags_to_create:
                new_tag = Tag(name=tag_name)
                new_tags.append(new_tag)
                existing_tags[tag_name] = new_tag

            session.add_all(new_tags)
            await session.flush()  # Сохраняем, чтобы получить IDs
        return existing_tags


class Category(BaseModel):
    __tablename__ = "categories"

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, )
    name: orm.Mapped[str] = orm.mapped_column(sa.String(50), unique=True, comment='Имя')
    slug: orm.Mapped[str] = orm.mapped_column(sa.String(50), unique=True)

    # Отношение один-ко-многим к постам
    posts: orm.Mapped[t.List["Post"]] = orm.relationship(
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
    edit_date: orm.Mapped[datetime] = orm.mapped_column(sa.DateTime(timezone=True), nullable=True,
                                                        comment='Дата Изменения поста.')
    title: orm.Mapped[str] = orm.mapped_column(sa.String(settings.POST_TITLE_LENGTH), nullable=False,
                                               comment='Название поста.')
    message: orm.Mapped[str] = orm.mapped_column(sa.Text, nullable=False, comment='Сообщение из поста')
    author_id: orm.Mapped[int] = orm.mapped_column(sa.ForeignKey("users.id", comment='Автор поста'), nullable=True)
    category_id: orm.Mapped[int] = orm.mapped_column(sa.ForeignKey("categories.id"), comment='Категория поста',
                                                     nullable=True)
    views: orm.Mapped[int] = orm.mapped_column(sa.Integer, nullable=True, comment="Количество просмотров")
    forwards: orm.Mapped[int] = orm.mapped_column(sa.Integer, nullable=True, comment="Количество пересылок")
    # media: Mapped[str] = mapped_column(Text, nullable=True, comment='Фото из поста')

    # Один к одному.
    author: orm.Mapped['User'] = orm.relationship("User", back_populates="posts")
    category: orm.Mapped[Category] = orm.relationship("Category", back_populates="posts")
    tags: orm.Mapped[t.List["Tag"]] = orm.relationship(
        "Tag",
        secondary=post_tags,
        back_populates="posts",
        lazy="selectin",
    )

    def __str__(self):
        return self.title

    @classmethod
    async def get_last_post(cls, session) -> 'Post':
        query = sa.select(cls).order_by(cls.date.desc()).limit(1)
        result = await session.execute(query)
        return result.scalar_one_or_none()


class AnimalGender(Enum):
    """Пол животного"""
    MALE = 'male'
    FEMALE = 'female'


# class Photo(BaseModel):
#     __tablename__ = "photos"
#
#     id: orm.Mapped[int] = orm.mapped_column(
#         sa.Integer, primary_key=True, nullable=False, unique=True
#     )
#     file_name: orm.Mapped[str] = orm.mapped_column(sa.String(255), nullable=False, comment='Название файла')
#     file_path: orm.Mapped[str] = orm.mapped_column(sa.String(255), nullable=False, comment='Путь сохранения файла')
#     ad:

# class CatAd(BaseModel):
#     """Объявление о продаже котика"""
#     __tablename__ = "cat_ads"
#     id: orm.Mapped[int] = orm.mapped_column(
#         sa.Integer, primary_key=True, nullable=False, unique=True
#     )
#     ad_id: orm.Mapped[int] = orm.mapped_column(
#         sa.Integer, sa.ForeignKey('ads.id'), nullable=False
#     )
#     ad: orm.Mapped['Ad'] = orm.relationship('Ad', back_populates="cat_ads")
#     gender: orm.Mapped[AnimalGender] = orm.mapped_column(
#         sa.Enum(AnimalGender, name='gender_enum'),
#         nullable=False,
#         comment='Пол животного'
#     )
#     birthdate: orm.Mapped[date] = orm.mapped_column(sa.Date, comment='Дата рождения')
#     color: orm.Mapped[str] = orm.mapped_column(
#         sa.String(100), nullable=False, comment='Окрас животного'
#     )
#     cattery: orm.Mapped[str] = orm.mapped_column(
#         sa.String(100), nullable=True, comment='Питомник'
#     )
#     price: orm.Mapped[Decimal] = orm.mapped_column(sa.DECIMAL(precision=12, scale=2), nullable=False, comment='Цена')
#     contacts: orm.Mapped[str] = orm.mapped_column(
#         sa.String(100), nullable=False, comment='Контактная информация'
#     )
#     photo_id: orm.Mapped[int] = orm.mapped_column(
#         sa.Integer, sa.ForeignKey('photos.id'), nullable=False
#     )
#     photo: orm.Mapped[t.List[Photo]] = orm.relationship('Photo')

class Photo(BaseModel):
    __tablename__ = "photos"

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    file_name: orm.Mapped[str] = orm.mapped_column(sa.String(255))
    file_path: orm.Mapped[str] = orm.mapped_column(sa.String(500))

    # ✅ Связь с объявлением
    ad_id: orm.Mapped[int] = orm.mapped_column(sa.ForeignKey('ads.id'))
    ad: orm.Mapped['Ad'] = orm.relationship('Ad', back_populates='photos')

    # Дополнительные поля
    sort_order: orm.Mapped[int] = orm.mapped_column(default=0)
    is_primary: orm.Mapped[bool] = orm.mapped_column(default=False)

class AdType(BaseModel):
    """Тип объявления"""
    __tablename__ = "ads_type"
    id: orm.Mapped[int] = orm.mapped_column(
        sa.Integer, primary_key=True, nullable=False, unique=True
    )
    name: orm.Mapped[str] = orm.mapped_column(
        sa.String(100), nullable=False, comment='Тип объявления'
    )
    description: orm.Mapped[t.Optional[str]] = orm.mapped_column(sa.Text, nullable=True)
    ads: orm.Mapped[t.List['Ad']] = orm.relationship('Ad', back_populates="ad_type")


class Ad(BaseModel):
    __tablename__ = "ads"

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    author_id: orm.Mapped[int] = orm.mapped_column(sa.ForeignKey('users.id'))
    ad_type_id: orm.Mapped[int] = orm.mapped_column(sa.ForeignKey('ad_types.id'))
    title: orm.Mapped[str] = orm.mapped_column(sa.String(200))
    attributes: orm.Mapped[dict] = orm.mapped_column(
        JSONB,
        nullable=False,
        default=dict
    )
    price: orm.Mapped[Decimal] = orm.mapped_column(sa.Numeric(12, 2))
    contacts: orm.Mapped[str] = orm.mapped_column(sa.String(200))
    photos: orm.Mapped[list['Photo']] = orm.relationship(
        'Photo',
        back_populates='ad',
        cascade='all, delete-orphan',  # автоматическое управление
        order_by='Photo.sort_order'
    )
    ad_type: orm.Mapped['AdType'] = orm.relationship('AdType')

    __table_args__ = (
        sa.Index('ix_ads_attributes_gin', 'attributes', postgresql_using='gin'),
    )
