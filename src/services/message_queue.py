import contextlib

import pika
from pika.adapters.blocking_connection import BlockingChannel

from message_queue_events.base import MessageQueueEvent

__all__ = (
    'get_message_queue_channel',
    'send_json_message',
)


@contextlib.contextmanager
def get_message_queue_channel(rabbitmq_url: str) -> BlockingChannel:
    params = pika.URLParameters(rabbitmq_url)
    with pika.BlockingConnection(params) as connection:
        channel = connection.channel()
        channel.queue_declare('telegram-notifications')
        yield channel


def send_json_message(channel: BlockingChannel, event: MessageQueueEvent):
    channel.basic_publish(
        exchange='',
        routing_key='telegram-notifications',
        body=event.as_bytes(),
    )