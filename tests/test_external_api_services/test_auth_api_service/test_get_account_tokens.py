import pytest

from core import exceptions


@pytest.mark.parametrize(
    'account_name, access_token, refresh_token',
    [
        (
                'account_vorkuta_1',
                'I8W05XMI09QJ3VV30YQ9JZQ29NNZ1KC8COJR7ODBIVPQ96O490',
                'WYWIPEJ0A52V02GALZ49TL7Z3DK0CBANME0Q0CW1C4RZ4FRF0T'
        ),
        (
                'account_saransk',
                'GKQEURVUXDTUQIAWFOJXPTTXVL8EKV5HUQT8ZOSAV6Y074TTBU',
                'V8Z2GEGX8VD73WBXSOHV6LIPNC7ZEMN9OHOS3VPQS6R8GW9MF5',
        ),
        (
                'account_syzran',
                'G1QB0OFI9M5402RB4PKU88Q9H1XVLV9YW34UNDGWHSUKVL8E3U',
                'ZC5G9NZKHOFU6AXE96MME739QSGZNAPB7YKBASCIPQO7H2LCDP',
        )
    ]
)
def test_auth_api_service_get_account_tokens(httpx_mock, auth_api, account_name, access_token, refresh_token):
    response_data = {
        'account_name': account_name,
        'access_token': access_token,
        'refresh_token': refresh_token,
    }
    httpx_mock.add_response(status_code=200, json=response_data)
    account_tokens = auth_api.get_account_tokens(account_name=account_name)
    assert account_tokens.account_name == account_name
    assert account_tokens.access_token == access_token
    assert account_tokens.refresh_token == refresh_token


def test_auth_api_service_get_account_tokens_raises_auth_credentials_not_found_error(httpx_mock, auth_api):
    httpx_mock.add_response(status_code=404)
    account_name = 'account_saransk'
    with pytest.raises(exceptions.AuthCredentialsNotFoundError) as error:
        auth_api.get_account_tokens(account_name=account_name)
    assert error.value.account_name == account_name


@pytest.mark.parametrize(
    'status_code',
    [
        400, 401, 403, 500, 502
    ]
)
def test_auth_api_service_get_account_tokens_raises_auth_api_error(httpx_mock, auth_api, status_code):
    httpx_mock.add_response(status_code=status_code)
    account_name = 'account_vyazma'
    with pytest.raises(exceptions.AuthAPIServiceError) as error:
        auth_api.get_account_tokens(account_name=account_name)
    assert not isinstance(error.value, exceptions.AuthCredentialsNotFoundError)
    assert error.value.account_name == account_name
