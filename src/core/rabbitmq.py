import json

import pika

from core import models
from config import get_app_settings
from core.utils import logger

__all__ = (
    'add_notification_to_queue',
    'close_rabbitmq_connection',
)

connection = pika.BlockingConnection(pika.URLParameters(get_app_settings().rabbitmq_url))
channel = connection.channel()
channel.queue_declare(queue='telegram-notifications')


def add_notification_to_queue(body: models.Event):
    channel.basic_publish(exchange='', routing_key='telegram-notifications',
                          body=json.dumps(body, default=str).encode('utf-8'))


def close_rabbitmq_connection():
    connection.close()
    logger.debug('RabbitMQ connection has been closed')
