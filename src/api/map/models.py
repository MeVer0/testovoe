from sqlalchemy import ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import relationship

from src.models import Base, intpk, varchar_255


class CityOrm(Base):

    __tablename__ = 'city'

    id: Mapped[intpk]
    # Лучше во всём проекте придерживаться одного стиля для кавычек (лучше ')
    region_id: Mapped[int] = mapped_column(ForeignKey("region.id"))
    name: Mapped[varchar_255]

    # Добавляем связь один ко многим с таблицей StreetOrm
    streets = relationship('StreetOrm', backref='city', lazy='dynamic')

    __table_args__ = (
        UniqueConstraint('region_id', 'name'),
        Index('idx_city_name', 'name')
    )


class StreetOrm(Base):

    __tablename__ = 'street'

    id: Mapped[intpk]
    city_id: Mapped[int] = mapped_column(ForeignKey("city.id"))
    name: Mapped[varchar_255]

    __table_args__ = (
        UniqueConstraint('city_id', 'name'),
        Index('idx_street_name', 'name')
    )


class RegionOrm(Base):

    __tablename__ = 'region'

    id: Mapped[intpk]
    name: Mapped[varchar_255] = mapped_column(unique=True)

    cities = relationship('CityOrm', backref='region', lazy='dynamic')

    __table_args__ = (UniqueConstraint('name'),)
