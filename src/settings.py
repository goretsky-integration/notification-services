import pathlib
from functools import lru_cache

from pydantic import BaseSettings, Field

__all__ = (
    'get_app_settings',
    'ROOT_PATH',
)

ROOT_PATH = pathlib.Path(__file__).parent.parent


class AppSettings(BaseSettings):
    debug: bool = Field(env='DEBUG')
    log_file_base_path: str | None = Field(env='LOG_FILE_BASE_PATH')
    rabbitmq_url: str = Field(env='RABBITMQ_URL')
    database_api_base_url: str = Field(env='DATABASE_API_BASE_URL')
    auth_service_base_url: str = Field(env='AUTH_SERVICE_BASE_URL')
    dodo_api_base_url: str = Field(env='DODO_API_BASE_URL')


@lru_cache
def get_app_settings() -> AppSettings:
    return AppSettings()
