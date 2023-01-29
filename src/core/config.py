import pathlib
import tomllib
from dataclasses import dataclass

__all__ = (
    'MessageQueueConfig',
    'PartialIngredientStopSalesConfig',
    'CheatedOrdersConfig',
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
class PartialIngredientStopSalesConfig:
    disallowed_ingredient_names: set[str]
    allowed_ingredient_names: set[str]


@dataclass(frozen=True, slots=True)
class CheatedOrdersConfig:
    skipped_phone_numbers: set[str]


@dataclass(frozen=True, slots=True)
class LoggingConfig:
    level: str
    file_path: str


@dataclass(frozen=True, slots=True)
class Config:
    country_code: str
    logging: LoggingConfig
    message_queue: MessageQueueConfig
    partial_ingredients: PartialIngredientStopSalesConfig
    cheated_orders: CheatedOrdersConfig
    api: APIConfig


def load_config(config_file_path: str | pathlib.Path) -> Config:
    with open(config_file_path, 'rb') as file:
        config = tomllib.load(file)
    return Config(
        country_code=config['country_code'],
        logging=LoggingConfig(
            level=config['logging']['level'],
            file_path=config['logging']['file_path'],
        ),
        api=APIConfig(
            auth_api_base_url=config['api']['auth_api_url'],
            dodo_api_base_url=config['api']['dodo_api_url'],
            database_api_base_url=config['api']['database_api_url'],
        ),
        partial_ingredients=PartialIngredientStopSalesConfig(
            allowed_ingredient_names=set(config['partial_ingredient_stop_sales']['allowed_ingredient_names']),
            disallowed_ingredient_names=set(config['partial_ingredient_stop_sales']['disallowed_ingredient_names']),
        ),
        cheated_orders=CheatedOrdersConfig(
            skipped_phone_numbers=set(config['cheated_orders']['skipped_phone_numbers']),
        ),
        message_queue=MessageQueueConfig(
            rabbitmq_url=config['message_queue']['rabbitmq_url'],
        ),
    )
