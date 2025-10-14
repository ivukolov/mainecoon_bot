import typing as t
from dataclasses import dataclass


@dataclass(frozen=True)
class AdsTypes:
    slug: str
    name: str
    description: str


CAT_ADS: t.Final[AdsTypes] = AdsTypes(
    slug='cat_ads',
    name='Реклама котиков',
    description='Рекламные посты по продаже котиков'
)