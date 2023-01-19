import pathlib
import tomllib
from dataclasses import dataclass

__all__ = (
    'MessageQueueConfig',
    'Config',
    'APIConfig',
    'load_config',
)


@dataclass(frozen=True, slots=True)
class MessageQueueConfig:
    rabbitmq_url: str


@dataclass(frozen=True, slots=True)
class APIConfig:
    dodo_api_base_url: str
    database_api_base_url: str
    auth_api_base_url: str


@dataclass(frozen=True, slots=True)
class Config:
    message_queue: MessageQueueConfig
    api: APIConfig


def load_config(config_file_path: str | pathlib.Path) -> Config:
    with open(config_file_path, 'rb') as file:
        config = tomllib.load(file)
    return Config(
        api=APIConfig(
            auth_api_base_url=config['api']['auth_api_url'],
            dodo_api_base_url=config['api']['dodo_api_url'],
            database_api_base_url=config['api']['database_api_url'],
        ),
        message_queue=MessageQueueConfig(
            rabbitmq_url=config['message_queue']['rabbitmq_url'],
        ),
    )
