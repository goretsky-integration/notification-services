from typing import TypeAlias

from pydantic import BaseModel

__all__ = (
    'Cookies',
    'AuthCookies',
    'AuthToken',
)

Cookies: TypeAlias = dict[str, str]


class AuthCookies(BaseModel):
    account_name: str
    cookies: Cookies


class AuthToken(BaseModel):
    account_name: str
    access_token: str
