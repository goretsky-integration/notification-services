import pika.exceptions
import redis

import db
import models
from services import api
from utils import logger


def add_canceled_order_message(
        storage: db.CanceledOrderUUIDsStorage,
        order: models.OrderByUUID,
        names_to_ids: dict[str, int],
):
    try:
        storage.add_uuid(order.uuid)
        db.add_notification_to_queue({
            'unit_id': names_to_ids[order.unit_name],
            'type': 'CANCELED_ORDERS',
            'payload': order.dict(),
        })
    except pika.exceptions.AMQPError:
        storage.remove_uuid(order.uuid)
        logger.warning(f'Order with UUID {order.uuid.hex} has not been added into rabbitmq')
    except redis.exceptions.RedisError:
        logger.warning(f'Order UUID {order.uuid.hex} has not been added into redis')
    else:
        logger.debug(f'Order with UUID {order.uuid.hex} has been added')


def main():
    shift_manager_accounts = db.get_shift_manager_accounts()
    all_units = db.get_units()
    names_to_ids = all_units.names_to_ids
    for account_name in shift_manager_accounts:
        storage = db.CanceledOrderUUIDsStorage(account_name)
        cookies = db.get_cookies(account_name)
        canceled_orders = api.get_canceled_orders(cookies)
        for order in canceled_orders:
            if order.receipt_printed_at is None:
                continue
            if storage.is_exist(order.uuid):
                continue
            add_canceled_order_message(storage, order, names_to_ids)


if __name__ == '__main__':
    main()
