from contextlib import asynccontextmanager

from src.config import db_user, db_host, db_name, db_password
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker


DATABASE_URL = f"postgresql+asyncpg://{db_user}:{db_password}@{db_host}/{db_name}"

engine = create_async_engine(
    DATABASE_URL,
    echo=True
)


def async_session_generator():
    return async_sessionmaker(engine, expire_on_commit=False)


@asynccontextmanager
async def get_async_session():
    try:
        async_session = async_session_generator()
        async with async_session() as session:
            yield session
    except:
        await session.rollback()
        raise
    finally:
        await session.close()

