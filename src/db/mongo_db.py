from pymongo import MongoClient

import models
from config import app_settings
from utils import logger
from utils.convert_models import UnitsConverter

__all__ = (
    'close_mongo_db_connection',
    'get_units',
    'get_shift_manager_accounts',
)

connection = MongoClient(app_settings.mongo_url)
db = connection.dodo


def close_mongo_db_connection():
    connection.close()
    logger.debug('Mongodb connection has been closed')


def get_shift_manager_accounts() -> set[str]:
    accounts = db.accounts.find({'name': {'$regex': r'^shift'}}, {'name': 1, '_id': 0})
    return {account['name'] for account in accounts}


def get_units() -> UnitsConverter:
    all_units_json = db.units.find({})
    units = [models.Unit.parse_obj(result) for result in all_units_json]
    return UnitsConverter(units=units)
