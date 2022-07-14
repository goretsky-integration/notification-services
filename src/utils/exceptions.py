class NoCookiesInDBError(Exception):

    def __init__(self, *args, account_name: str):
        super().__init__(*args)
        self.account_name = account_name


class NoTokenInDBError(Exception):

    def __init__(self, *args, account_name: str):
        super().__init__(*args)
        self.account_name = account_name


class DodoAPIError(Exception):
    pass


class CanceledOrderPublishError(Exception):
    pass
