from dataclasses import dataclass
from typing import TypeVar, Generic

from pydantic import BaseModel

__all__ = (
    'AccountTokens',
    'AccountCookies',
    'AccountsCredentialsBatchResponse',
)

AccountCredentialsT = TypeVar('AccountCredentialsT')


class AccountTokens(BaseModel):
    account_name: str
    access_token: str
    refresh_token: str


class AccountCookies(BaseModel):
    account_name: str
    cookies: dict[str, str]


@dataclass(frozen=True, slots=True)
class AccountsCredentialsBatchResponse(Generic[AccountCredentialsT]):
    result: list[AccountCredentialsT]
    errors: list[str]
