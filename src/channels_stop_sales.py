import atexit

import db
from services import api


@atexit.register
def on_shutdown():
    db.close_redis_db_connection()
    db.close_mongo_db_connection()
    db.close_rabbitmq_connection()


def main():
    units = db.get_units()
    for account_name, unit_uuids in units.account_names_to_unit_uuids.items():
        access_token = db.get_token(account_name)
        response = api.get_stop_sales_by_channels(access_token, unit_uuids)
        for stop_sale in response:
            if stop_sale.staff_name_who_resumed is not None:
                continue
            body = {
                'type': 'PIZZERIA_STOP_SALES',
                'unit_id': units.uuids_to_ids[stop_sale.unit_id],
                'payload': stop_sale.dict(include={'unit_name', 'started_at', 'reason', 'sales_channel_name'})
            }
            db.add_notification_to_queue(body)


if __name__ == '__main__':
    main()
