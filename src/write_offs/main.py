import asyncio
import json
import os
from typing import Generator
from uuid import UUID

import httpx
from dodolib import DatabaseClient
from dotenv import load_dotenv

load_dotenv()

import models
import rabbitmq

WRITE_OFFS_API_URL = f'{os.getenv("WRITE_OFFS_API_URL")}/write-offs/events/'


def parse_event(body: str) -> models.PingEvent | models.WriteOffEvent:
    event_type = None
    event_id = None
    data = None
    for body_line in body.strip().splitlines():
        match body_line.split(': '):
            case ['event', other]:
                event_type = other
            case ['data', *other]:
                data = json.loads(': '.join(other).replace("'", '"'))
            case ['id', other]:
                event_id = UUID(other)
    return (models.PingEvent(type=event_type, data=data)
            if event_type == 'ping'
            else models.WriteOffEvent(id=event_id, type=event_type, data=data))


def run_events_stream() -> Generator[models.WriteOffEvent, None, None]:
    while True:
        with (
            httpx.Client(timeout=30) as client,
            client.stream('GET', WRITE_OFFS_API_URL) as stream,
        ):
            for text in stream.iter_text():
                yield parse_event(text)


async def main():
    async with DatabaseClient() as client:
        units = await client.get_units()
    unit_id_to_name = {unit.id: unit.name for unit in units}
    for event in run_events_stream():
        if event.type == 'ping':
            continue
        unit_id = event.data['unit_id']
        body = {
            'type': 'WRITE_OFFS',
            'unit_id': unit_id,
            'payload': {
                'event_type': event.type,
                'unit_name': unit_id_to_name[unit_id],
            }
        }
        rabbitmq.add_notification_to_queue(body)


if __name__ == '__main__':
    asyncio.run(main())
