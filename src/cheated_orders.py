import db
from services import api
from utils import logger

FILTER_NUMBERS = {
    '+7 968 032-59-99',
}


def main():
    all_units = db.get_units()
    unit_names_to_ids = all_units.names_to_ids
    for account_name, units in all_units.account_names_to_units.items():
        storage = db.CheatedPhoneNumbersCountStorage(account_name)
        cookies = db.get_cookies(account_name)
        cheated_orders = api.get_cheated_orders(cookies, units.ids_and_names)
        for cheated_order in cheated_orders:
            if cheated_order.phone_number in FILTER_NUMBERS:
                continue
            if cheated_order.orders_count <= storage.get_count(cheated_order.phone_number):
                continue
            db.add_notification_to_queue({
                'unit_id': unit_names_to_ids[cheated_order.unit_name],
                'type': 'CHEATED_PHONE_NUMBERS',
                'payload': cheated_order.dict()
            })
            storage.set_count(cheated_order.phone_number, cheated_order.orders_count)
            logger.debug(f'New cheated order {cheated_order.phone_number}')


if __name__ == '__main__':
    main()
