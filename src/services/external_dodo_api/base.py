from typing import TypeAlias

import httpx

__all__ = ('APIService',)

HTTPClient: TypeAlias = httpx.Client


class APIService:
    __slots__ = ('_client',)

    def __init__(self, client: HTTPClient):
        self._client = client
