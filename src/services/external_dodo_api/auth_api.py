import models
from core import exceptions
from services.external_dodo_api.base import APIService

__all__ = ('AuthAPI',)


class AuthAPI(APIService):

    def get_account_tokens(self, account_name: str) -> models.AccountTokens:
        request_query_params = {'account_name': account_name}
        response = self._client.get('/auth/token/', params=request_query_params)
        if response.is_success:
            response_data = response.json()
            return models.AccountTokens.parse_obj(response_data)
        elif response.status_code == 404:
            raise exceptions.AuthCredentialsNotFoundError(account_name=account_name)
        raise exceptions.AuthAPIServiceError(account_name=account_name)

    def get_account_cookies(self, account_name: str) -> models.AccountCookies:
        request_query_params = {'account_name': account_name}
        response = self._client.get('/auth/cookies/', params=request_query_params)
        if response.is_success:
            response_data = response.json()
            return models.AccountCookies.parse_obj(response_data)
        elif response.status_code == 404:
            raise exceptions.AuthCredentialsNotFoundError(account_name=account_name)
        raise exceptions.AuthAPIServiceError(account_name=account_name)
