import httpx

from utils import logger

__all__ = (
    'BaseHTTPService',
)


class BaseHTTPService:

    def __init__(self, base_url: str):
        self._client = httpx.AsyncClient(base_url=base_url, timeout=120)

    async def close(self):
        if not self._client.is_closed:
            await self._client.aclose()
            logger.debug(f'HTTP client of {self.__class__.__name__} been closed')

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
