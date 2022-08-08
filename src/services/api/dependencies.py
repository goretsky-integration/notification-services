from config import get_app_settings
from services.api.auth_credentials import AuthClient
from services.api.db_api import DatabaseClient
from services.api.dodo_api import DodoAPIClient

__all__ = (
    'get_db_client',
    'get_auth_client',
    'get_dodo_api_client',
)


def get_db_client() -> DatabaseClient:
    return DatabaseClient(get_app_settings().db_api_url)


def get_auth_client() -> AuthClient:
    return AuthClient(get_app_settings().db_api_url)


def get_dodo_api_client() -> DodoAPIClient:
    return DodoAPIClient(get_app_settings().api_url)
