import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.orm import sessionmaker

from src.main import Base, app, get_session

DATABASE_URL: str = "sqlite+aiosqlite:///"


engine: AsyncEngine = create_async_engine(DATABASE_URL, echo=False)
async_session: sessionmaker = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)


async def get_session_override() -> AsyncSession:
    session: AsyncSession
    async with async_session() as session:
        yield session


app.dependency_overrides[get_session] = get_session_override


@pytest.fixture(scope="module")
async def db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    await engine.dispose()


@pytest.fixture
async def client(db) -> AsyncClient:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://127.0.0.1:8000"
    ) as client:
        yield client
