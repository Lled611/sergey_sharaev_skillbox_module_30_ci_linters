import pytest
from fastapi.testclient import TestClient

from src.main import app


client: TestClient = TestClient(app)


@pytest.mark.parametrize('route', [
    '/recipes',
    '/recipes/1'
])
def test_route_status(route: str) -> None:
    response = client.get(route)

    assert response.status_code == 200
