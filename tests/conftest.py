import pytest
from httpx import ASGITransport, AsyncClient

from app.dependencies import get_url_repository
from app.main import app


@pytest.fixture
async def test_client(mock_url_repository):
    app.dependency_overrides[get_url_repository] = lambda: mock_url_repository
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture
def mock_url_repository(mocker):
    mock = mocker.Mock()
    return mock
