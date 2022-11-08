import json
from typing import TypedDict

import pika
from pika.adapters.blocking_connection import BlockingChannel

__all__ = (
    'get_message_queue_channel',
    'send_json_message',
)


class Message(TypedDict):
    unit_id: int
    type: str
    payload: dict | list


def get_message_queue_channel() -> BlockingChannel:
    params = pika.ConnectionParameters(port=5672)
    with pika.BlockingConnection(params) as connection:
        channel = connection.channel()
        channel.queue_declare('telegram-notifications')
        yield channel


def send_json_message(channel: BlockingChannel, data: Message):
    channel.basic_publish(
        exchange='',
        routing_key='telegram-notifications',
        body=json.dumps(data, default=str).encode('utf-8'),
    )
