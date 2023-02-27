class ApplicationError(Exception):
    pass


class AuthAPIServiceError(ApplicationError):

    def __init__(self, *args, account_name: str):
        super().__init__(*args)
        self.account_name = account_name


class AuthCredentialsNotFoundError(AuthAPIServiceError):
    pass
