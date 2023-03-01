import logging
from typing import TypeVar, Callable, Iterable

import models
from core import exceptions

__all__ = ('get_account_credentials_batch',)

AccountCredentialsT = TypeVar('AccountCredentialsT')


def get_account_credentials_batch(
        *,
        retrieve_account_credentials: Callable[[str], AccountCredentialsT],
        account_names: Iterable[str],
        attempts_count: int = 3
) -> models.AccountsCredentialsBatchResponse[AccountCredentialsT]:
    """Safely get account credentials (both cookies and tokens).

    Args:
        retrieve_account_credentials: Callback with following signature:
                                        account names on the input,
                                        credentials on the output.
        account_names: Collection of account names.
        attempts_count: Attempts number to retrieve credentials for each account.

    Returns:
        Collection of account credentials.
        Also, it returns collection of account names which credentials could not be retrieved.
    """
    result: list[AccountCredentialsT] = []
    errors: list[str] = []

    for account_name in account_names:
        for _ in range(attempts_count):
            try:
                account_cookies = retrieve_account_credentials(account_name)
            except exceptions.AuthCredentialsNotFoundError:
                logging.exception(f'Auth credentials for {account_name} has not found. Trying again')
            except exceptions.AuthAPIServiceError:
                logging.exception(f'Unexpected error while retrieving credentials for {account_name}. Trying again')
            else:
                result.append(account_cookies)
                break
        else:
            errors.append(account_name)
            logging.error(f'Could not eventually retrieve auth credentials for {account_name}')

    return models.AccountsCredentialsBatchResponse(result=result, errors=errors)
