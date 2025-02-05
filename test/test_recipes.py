import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_recipe(client: AsyncClient) -> None:
    response = await client.post('/recipes', json={
        "name": "bread",
        "description": "bread",
        "cooking_time": 1,
        "ingredients": [
            {
                "product": {
                "name": "bread"
            },
                "count": 1
            }
        ]
    })

    assert response.status_code == 204


@pytest.mark.parametrize('route', [
    '/recipes',
    '/recipes/1'
])
@pytest.mark.asyncio
async def test_route_status(client: AsyncClient, route: str) -> None:
    response = await client.get(route)

    assert response.status_code == 200
