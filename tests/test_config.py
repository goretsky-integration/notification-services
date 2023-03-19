import io
import pathlib
import tempfile

import models
from core.config import load_config_from_file, load_config_from_string, load_config_from_bytes


def test_load_config_from_string(config_string: str, expected_config: models.Config):
    assert load_config_from_string(config_string) == expected_config


def test_load_config_from_bytes(config_string: str, expected_config: models.Config):
    config_bytes = io.BytesIO(config_string.encode('utf-8'))
    assert load_config_from_bytes(config_bytes) == expected_config


def test_load_config_from_file(config_string: str, expected_config: models.Config):
    with tempfile.NamedTemporaryFile(suffix='.toml', delete=False) as file:
        file_path = pathlib.Path(file.name)
    try:
        file_path.write_bytes(config_string.encode('utf-8'))
        assert load_config_from_file(file_path) == expected_config
    finally:
        file_path.unlink(missing_ok=True)
