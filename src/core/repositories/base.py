import httpx

from core.utils import logger

__all__ = (
    'BaseHTTPAPIRepository',
)


class BaseHTTPAPIRepository:

    def __init__(self, base_url: str):
        self._client = httpx.Client(base_url=base_url, timeout=60)

    def close(self):
        if not self._client.is_closed:
            self._client.close()
            logger.debug(f'HTTP client of {self.__class__.__name__} been closed')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
