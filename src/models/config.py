from dataclasses import dataclass

__all__ = (
    'MessageQueueConfig',
    'CheatedOrdersConfig',
    'APIConfig',
    'LoggingConfig',
    'PartialIngredientStopSalesConfig',
    'Config',
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
