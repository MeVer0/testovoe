import datetime
from sqlalchemy import UniqueConstraint, Index
from sqlalchemy.orm import Mapped, relationship

from src.models import Base, intpk, varchar_50, varchar_10


class ShopOrm(Base):

    __tablename__ = 'shop'

    id: Mapped[intpk]
    name: Mapped[varchar_50]
    city_id: Mapped[int]
    street_id: Mapped[int]
    building: Mapped[varchar_10]
    open_time: Mapped[datetime.time]
    close_time: Mapped[datetime.time]

    __table_args__ = (
        UniqueConstraint('city_id', 'street_id', 'building'),
        Index('idx_open_close_time', 'open_time', 'close_time'),
        Index('idx_shop_name', 'name')
    )

    city = relationship('CityOrm', lazy='raise')
    street = relationship('StreetOrm', lazy='raise')
