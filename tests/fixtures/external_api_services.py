import httpx
import pytest

from services.external_dodo_api import AuthAPI


@pytest.fixture
def http_client() -> httpx.Client:
    with httpx.Client(base_url='http://localhost:8000') as client:
        yield client


@pytest.fixture
def auth_api(http_client) -> AuthAPI:
    yield AuthAPI(http_client)
