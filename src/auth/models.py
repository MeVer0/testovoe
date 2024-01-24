from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from pydantic import EmailStr
from sqlalchemy.orm import Mapped

from src.models import intpk, Base


class User(SQLAlchemyBaseUserTable[int], Base):
    id: Mapped[intpk]
    email: EmailStr
    username: Mapped[str]
    hashed_password: Mapped[str]
    is_active: Mapped[bool]
    is_superuser: Mapped[bool]
    is_verified: Mapped[bool]
