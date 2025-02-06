from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncAttrs, AsyncSession, create_async_engine
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL: str = "sqlite+aiosqlite:///./recipes.db"


engine: AsyncEngine = create_async_engine(DATABASE_URL, echo=False)
async_session: sessionmaker = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    session: AsyncSession
    async with async_session() as session:
        yield session


class Base(AsyncAttrs, DeclarativeBase): ...
