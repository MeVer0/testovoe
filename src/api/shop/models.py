import datetime
from typing import Annotated
from sqlalchemy import ForeignKey, UniqueConstraint, Index, VARCHAR, Time
from sqlalchemy.orm import Mapped, mapped_column

from src.models import Base, intpk, varchar_50, varchar_10, date_create_truncated


class ShopOrm(Base):

    __tablename__ = 'shop'

    id: Mapped[intpk]
    name: Mapped[varchar_50]
    city_id: Mapped[int]
    street_id: Mapped[int]
    building: Mapped[varchar_10]
    open_time: Mapped[datetime.time]
    close_time: Mapped[datetime.time]

    __table_args__ = (UniqueConstraint('city_id', 'street_id', 'building'),)
    __table_args__ += (Index('idx_open_close_time', 'open_time', 'close_time'),)
    __table_args__ += (Index('idx_shop_name', 'name'),)