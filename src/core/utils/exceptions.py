"""
- DatabaseAPIError
    - AuthCredentialsAPIError
        - NoCookiesError
        - NoTokenError
- DodoAPIError
"""


class DodoAPIError(Exception):
    pass


class DatabaseAPIError(Exception):
    pass


class AuthCredentialsAPIError(DatabaseAPIError):

    def __init__(self, *args, account_name: str):
        super().__init__(*args)
        self.account_name = account_name


class NoCookiesError(AuthCredentialsAPIError):
    pass


class NoTokenError(AuthCredentialsAPIError):
    pass
