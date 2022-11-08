from loguru import logger

from settings import get_app_settings, ROOT_PATH

__all__ = (
    'logger',
)

log_level = 'DEBUG' if get_app_settings().debug else 'INFO'
log_file_path = get_app_settings().log_file_base_path
if log_file_path is None:
    log_file_path = ROOT_PATH / 'logs.log'
logger.add(log_file_path, level=log_level)
