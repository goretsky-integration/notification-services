import json
import os
from typing import TypedDict

import pika

__all__ = (
    'add_notification_to_queue',
    'close_rabbitmq_connection',
)

connection = pika.BlockingConnection(pika.URLParameters(os.getenv('RABBITMQ_URL')))
channel = connection.channel()
channel.queue_declare(queue='telegram-notifications')


class Event(TypedDict):
    type: str
    unit_id: int
    payload: dict


def add_notification_to_queue(body: Event):
    channel.basic_publish(exchange='', routing_key='telegram-notifications',
                          body=json.dumps(body, default=str).encode('utf-8'))


def close_rabbitmq_connection():
    connection.close()
