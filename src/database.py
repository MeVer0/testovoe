from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.config import db_user, db_host, db_name, db_password


DATABASE_URL = f"postgresql+asyncpg://{db_user}:{db_password}@{db_host}/{db_name}"

engine = create_async_engine(
    DATABASE_URL,
    echo=True
)


def async_session_generator():
    return async_sessionmaker(engine, expire_on_commit=False)


# Нет тайпинга и очевидного эксепшена
@asynccontextmanager
async def get_async_session() -> AsyncSession:
    try:
        async_session = async_session_generator()
        async with async_session() as session:
            yield session
    except Exception as e:
        await session.rollback()
        raise e
    finally:
        await session.close()

