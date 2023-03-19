import io
import pathlib
import tomllib

import models
from services.mappers import map_config_dto

__all__ = (
    'load_config_from_bytes',
    'load_config_from_string',
    'load_config_from_file',
)


def load_config_from_file(file_path: pathlib.Path) -> models.Config:
    with open(file_path, 'rb') as file:
        config = tomllib.load(file)
    return map_config_dto(config)


def load_config_from_bytes(config: io.BytesIO) -> models.Config:
    config = tomllib.load(config)
    return map_config_dto(config)


def load_config_from_string(config: str) -> models.Config:
    config = tomllib.loads(config)
    return map_config_dto(config)
