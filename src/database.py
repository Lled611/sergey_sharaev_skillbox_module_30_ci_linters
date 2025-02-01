from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncAttrs
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DATABASE_URL: str = "sqlite+aiosqlite:///./recipes.db"


engine: AsyncEngine = create_async_engine(DATABASE_URL, echo=True)
async_session: sessionmaker = sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession
)
session: AsyncSession = async_session()


class Base(AsyncAttrs, DeclarativeBase):
    ...
