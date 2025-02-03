import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.orm import sessionmaker

from src.main import app, get_session, Base


DATABASE_URL: str = "sqlite+aiosqlite:///"


engine: AsyncEngine = create_async_engine(DATABASE_URL, echo=False)
async_session: sessionmaker = sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession
)


async def get_session_override() -> AsyncSession:
    session: AsyncSession
    async with async_session() as session:
        yield session


app.dependency_overrides[get_session] = get_session_override


@pytest.mark.anyio
@pytest.mark.parametrize('route', [
    '/recipes',
    # '/recipes/1'
])
async def test_route_status(route: str) -> None:
    # with async_session() as session:
    # response = client.get(route)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url='http://127.0.0.1:8000'
    ) as ac:
        response = await ac.get(route)

    await engine.dispose()

    assert response.status_code == 200
