from config import get_app_settings
from core.repositories.auth_credentials import AuthCredentialsRepository
from core.repositories.db_api import DatabaseRepository
from core.repositories.dodo_api import DodoAPIRepository

__all__ = (
    'get_db_client',
    'get_auth_client',
    'get_dodo_api_client',
)


def get_db_client() -> DatabaseRepository:
    return DatabaseRepository(get_app_settings().db_api_url)


def get_auth_client() -> AuthCredentialsRepository:
    return AuthCredentialsRepository(get_app_settings().db_api_url)


def get_dodo_api_client() -> DodoAPIRepository:
    return DodoAPIRepository(get_app_settings().api_url)
