from services.http_client_factories import HTTPClient

__all__ = ('APIService',)


class APIService:
    __slots__ = ('_client',)

    def __init__(self, client: HTTPClient):
        self._client = client
