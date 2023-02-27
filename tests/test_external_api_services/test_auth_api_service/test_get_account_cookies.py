import pytest

from core import exceptions


@pytest.mark.parametrize(
    'account_name, cookies',
    [
        (
                'account_saratov',
                {'sessionId': 'EKuQfp3LWv3wJ2kLJnVMeWWyzgdeKfNCXtZfG7WOYk5Y9QDIt3'},
        ),
        (
                'account_spb',
                {'sessionId': 'SE8z4xGDkoxJlXjTFev68syie7D6Wv0Venr0vo1eEmzmNYydFc'},
        ),
    ],
)
def test_auth_api_service_get_account_cookies(httpx_mock, auth_api, account_name, cookies):
    response_data = {
        'account_name': account_name,
        'cookies': cookies,
    }
    httpx_mock.add_response(status_code=200, json=response_data)
    account_cookies = auth_api.get_account_cookies(account_name=account_name)
    assert account_cookies.account_name == account_name
    assert account_cookies.cookies == cookies


def test_auth_api_service_get_account_cookies_raises_auth_credentials_not_found_error(httpx_mock, auth_api):
    httpx_mock.add_response(status_code=404)
    account_name = 'account_saransk'
    with pytest.raises(exceptions.AuthCredentialsNotFoundError) as error:
        auth_api.get_account_cookies(account_name=account_name)
    assert error.value.account_name == account_name


@pytest.mark.parametrize(
    'status_code',
    [
        400, 401, 403, 500, 502
    ]
)
def test_auth_api_service_get_account_cookies_raises_auth_api_error(httpx_mock, auth_api, status_code):
    httpx_mock.add_response(status_code=status_code)
    account_name = 'account_vyazma'
    with pytest.raises(exceptions.AuthAPIServiceError) as error:
        auth_api.get_account_cookies(account_name=account_name)
    assert not isinstance(error.value, exceptions.AuthCredentialsNotFoundError)
    assert error.value.account_name == account_name
