from core import models
from core.repositories.base import BaseHTTPAPIRepository
from core.utils import exceptions

__all__ = (
    'AuthCredentialsRepository',
)


class AuthCredentialsRepository(BaseHTTPAPIRepository):

    def get_cookies(self, account_name: str) -> models.AuthCookies:
        response = self._client.get('/auth/cookies/', params={'account_name': account_name}, timeout=30)
        if response.status_code == 404:
            raise exceptions.NoCookiesError(account_name=account_name)
        return models.AuthCookies.parse_obj(response.json())

    def get_tokens(self, account_name: str) -> models.AuthToken:
        response = self._client.get('/auth/token/', params={'account_name': account_name}, timeout=30)
        if response.status_code == 404:
            raise exceptions.NoTokenError(account_name=account_name)
        return models.AuthToken.parse_obj(response.json())
