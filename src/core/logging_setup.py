import logging.handlers
import pathlib

__all__ = ('setup_logging',)


def setup_logging(*, loglevel: str | int = logging.WARNING, logfile_path: str | pathlib.Path | None = None) -> None:
    logging.basicConfig(
        level=loglevel,
        format='%(asctime)s\t| %(levelname)s\t | %(message)s',
        handlers=(
            logging.FileHandler(logfile_path),
            logging.StreamHandler(),
        )
    )
