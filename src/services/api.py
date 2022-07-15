import sys
import uuid
from typing import Iterable, TypeVar, Type

import httpx
from pydantic import parse_obj_as

import models
from config import app_settings
from utils import exceptions
from utils.logger import logger

SSM = TypeVar('SSM')


def ping():
    url = f'{app_settings.api_url}/ping'
    response = httpx.get(url)
    if not response.is_success:
        raise exceptions.DodoAPIError


def get_canceled_orders(cookies: dict) -> list[models.OrderByUUID]:
    url = f'{app_settings.api_url}/v1/canceled-orders'
    body = {'cookies': cookies}
    response = httpx.post(url, json=body, timeout=30)
    if not response.is_success:
        raise exceptions.DodoAPIError
    return parse_obj_as(list[models.OrderByUUID], response.json())


def get_cheated_orders(cookies: dict, unit_ids_and_names) -> list[models.CheatedOrders]:
    url = f'{app_settings.api_url}/v1/cheated-orders'
    body = {'cookies': cookies, 'units': unit_ids_and_names, 'date': '2022-07-14'}
    response = httpx.post(url, json=body, timeout=30)
    if not response.is_success:
        raise exceptions.DodoAPIError
    return parse_obj_as(list[models.CheatedOrders], response.json())


class StopSalesByToken:

    def __init__(self, url: str, stop_sale_model: Type[SSM]):
        self._url = url
        self._stop_sale_model = stop_sale_model

    def __call__(self, token: str, unit_uuids: Iterable[uuid.UUID]) -> list[SSM]:
        params = {
            'unit_uuids': [str(unit_uuid) for unit_uuid in unit_uuids],
            'token': token,
        }
        response = httpx.get(self._url, params=params, timeout=30)
        if not response.is_success:
            raise exceptions.DodoAPIError
        return parse_obj_as(list[self._stop_sale_model], response.json())


get_stop_sales_by_ingredients = StopSalesByToken(
    url=f'{app_settings.api_url}/v2/stop-sales/ingredients',
    stop_sale_model=models.StopSaleByIngredients,
)

get_stop_sales_by_products = StopSalesByToken(
    url=f'{app_settings.api_url}/v2/stop-sales/products',
    stop_sale_model=models.StopSaleByProduct,
)

get_stop_sales_by_channels = StopSalesByToken(
    url=f'{app_settings.api_url}/v2/stop-sales/channels',
    stop_sale_model=models.StopSaleBySalesChannels,
)

try:
    ping()
except httpx.HTTPError:
    logger.critical('Could not connect to Dodo API')
    sys.exit(1)
