import json
import uuid

import redis

import models
from config import app_settings
from utils import logger, exceptions

__all__ = (
    'close_redis_db_connection',
    'get_token',
    'get_cookies',
    'CheatedPhoneNumbersCountStorage',
    'CanceledOrderUUIDsStorage',
)

connection = redis.from_url(app_settings.redis_url, decode_responses=True)

try:
    connection.ping()
except redis.exceptions.ConnectionError:
    logger.critical('Could not connect to redis')
    exit(1)


class CheatedPhoneNumbersCountStorage:
    storage_name = 'cheated_phone_numbers_count'

    def __init__(self, name: str):
        self._name = name

    @classmethod
    def clear(cls):
        return connection.delete(cls.storage_name)

    def set_count(self, phone_number: str, count: int) -> int:
        return connection.hset(self.storage_name, f'{self._name}@{phone_number}', count)

    def get_count(self, phone_number: str) -> int:
        count = connection.hget(self.storage_name, f'{self._name}@{phone_number}')
        if count is None:
            return 0
        return int(count)


class CanceledOrderUUIDsStorage:
    __slots__ = ('_storage_name',)

    def __init__(self, name: str):
        self._storage_name = f'canceled_orders@{name}'

    def add_uuid(self, *order_uuids: uuid.UUID) -> int:
        return connection.sadd(self._storage_name, *(order_uuid.hex for order_uuid in order_uuids))

    def remove_uuid(self, *order_uuids: uuid.UUID):
        return connection.srem(self._storage_name, *(order_uuid.hex for order_uuid in order_uuids))

    def is_exist(self, order_uuid: uuid.UUID) -> bool:
        return connection.sismember(self._storage_name, order_uuid.hex)

    def clear(self) -> int:
        return connection.delete(self._storage_name)


def get_token(account_name: models.AccessToken) -> models.AccessToken:
    token = connection.get(f'token_{account_name}')
    if token is None:
        raise exceptions.NoTokenInDBError(account_name=account_name)
    return token


def get_cookies(account_name: str) -> models.Cookies:
    cookies_json = connection.get(f'cookies_{account_name}')
    if cookies_json is None:
        raise exceptions.NoCookiesInDBError(account_name=account_name)
    return json.loads(cookies_json)


def close_redis_db_connection():
    connection.close()
    logger.debug('Redis connection has been closed')
