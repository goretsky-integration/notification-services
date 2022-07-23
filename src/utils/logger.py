from loguru import logger

from config import LOGS_FILE_PATH, app_settings

__all__ = (
    'logger',
)

log_level = 'DEBUG' if app_settings.debug else 'INFO'
logger.add(
    sink=LOGS_FILE_PATH,
    level=log_level,
    retention='3 days',
)
