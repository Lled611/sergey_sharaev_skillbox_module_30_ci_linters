# from typing import AsyncGenerator
# import pytest
# from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
# from sqlalchemy.ext.asyncio.engine import AsyncEngine, AsyncConnection, AsyncTransaction
#
# DATABASE_URL: str = "sqlite+aiosqlite:///"
#
#
# engine: AsyncEngine = create_async_engine(DATABASE_URL, echo=False)
#
#
# @pytest.fixture(scope="module")
# async def connection() -> AsyncGenerator[AsyncConnection, None]:
#     async with engine.connect() as connection:
#         yield connection
#
#
# @pytest.fixture(scope="module")
# async def transaction(connection: AsyncConnection) -> AsyncGenerator[AsyncTransaction, None]:
#     async with connection.begin() as transaction:
#         yield transaction
#
# @pytest.fixture
# async def session(connection: AsyncConnection, transaction: AsyncTransaction) -> AsyncGenerator[AsyncSession, None]:
#     async_session = AsyncSession(bind=connection)
