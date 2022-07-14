import logging.config

from config import LOGS_FILE_PATH

__all__ = (
    'logger',
)

log_config = {
    "version": 1,
    "root": {
        "handlers": ["console"],
        "level": "DEBUG"
    },
    "handlers": {
        "console": {
            "formatter": "std_out",
            "class": "logging.StreamHandler",
            "level": "DEBUG"
        }
    },
    "formatters": {
        "std_out": {
            "format": "%(asctime)s : %(levelname)s : %(module)s : %(funcName)s : %(lineno)d)\nLog : %(message)s",
            "datefmt": "%d-%m-%Y %I:%M:%S"
        }
    },
}

logging.config.dictConfig(log_config)
logger = logging.getLogger()
handler = logging.FileHandler(LOGS_FILE_PATH)
logger.addHandler(handler)
