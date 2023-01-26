from pydantic import BaseModel

__all__ = ('AccountTokens', 'AccountCookies')


class AccountTokens(BaseModel):
    account_name: str
    access_token: str
    refresh_token: str


class AccountCookies(BaseModel):
    account_name: str
    cookies: dict[str, str]
