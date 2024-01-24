from sqlalchemy.orm import DeclarativeBase, relationship

from datetime import datetime, time
from typing import Annotated

from sqlalchemy import text, VARCHAR, PrimaryKeyConstraint, Column, Integer, ForeignKey, Boolean
from sqlalchemy.orm import mapped_column


intpk = Annotated[int, mapped_column(primary_key=True, autoincrement=True)]
date_create = Annotated[datetime, mapped_column(server_default=text('CURRENT_TIMESTAMP()'))]
date_create_truncated = Annotated[time, mapped_column(server_default=text("date_trunc('minute', current_timestamp)"))]
varchar_10 = Annotated[str, mapped_column(type_=VARCHAR(10))]
varchar_50 = Annotated[str, mapped_column(type_=VARCHAR(50))]
varchar_255 = Annotated[str, mapped_column(type_=VARCHAR(255))]
varchar_1000 = Annotated[str, mapped_column(type_=VARCHAR(1000))]


class Base(DeclarativeBase):
    pass







