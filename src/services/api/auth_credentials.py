import models
from services.api.base import BaseHTTPService
from utils import exceptions

__all__ = (
    'AuthClient',
)


class AuthClient(BaseHTTPService):

    async def get_cookies(self, account_name: str) -> models.AuthCookies:
        response = await self._client.get('/auth/cookies/', params={'account_name': account_name}, timeout=30)
        if response.status_code == 404:
            raise exceptions.NoCookiesError(account_name=account_name)
        return models.AuthCookies.parse_obj(response.json())

    async def get_tokens(self, account_name: str) -> models.AuthToken:
        response = await self._client.get('/auth/token/', params={'account_name': account_name}, timeout=30)
        if response.status_code == 404:
            raise exceptions.NoTokenError(account_name=account_name)
        return models.AuthToken.parse_obj(response.json())
