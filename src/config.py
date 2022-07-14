import pathlib

from pydantic import BaseSettings, Field
from dotenv import load_dotenv

__all__ = (
    'app_settings',
    'ROOT_PATH',
    'LOGS_FILE_PATH',
    'LOCAL_STORAGE_PATH'
)

load_dotenv()

ROOT_PATH = pathlib.Path(__file__).parent.parent
LOGS_FILE_PATH = ROOT_PATH / 'logs.log'
LOCAL_STORAGE_PATH = ROOT_PATH / 'local_storage'


class AppSettings(BaseSettings):
    mongo_url: str = Field(..., env='MONGO_DB_URL')
    redis_url: str = Field(..., env='REDIS_DB_URL')
    debug: bool = Field(..., env='DEBUG')
    api_url: str = Field(..., env='API_URL')
    rabbitmq_url: str = Field(..., env='RABBITMQ_URL')


app_settings = AppSettings()
