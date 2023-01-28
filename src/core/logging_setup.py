import logging
import pathlib

__all__ = ('setup_logging',)


def setup_logging(*, loglevel: str | int = logging.WARNING, logfile_path: str | pathlib.Path | None = None) -> None:
    logging.basicConfig(filename=logfile_path, level=loglevel)
