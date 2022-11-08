import json
import pathlib

from uuid import UUID

from settings import ROOT_PATH

__all__ = (
    'UUIDStorage',
)

STORAGE_FILE_PATH = pathlib.Path.joinpath(
    ROOT_PATH,
    'local_storage',
    'canceled_order_uuids.json',
)


class UUIDStorage:

    def __init__(self):
        self.uuids = set()
        self.load()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.save()

    def __repr__(self):
        return f'{self.uuids}'

    def flush(self) -> None:
        self.save()
        self.load()

    def save(self) -> None:
        with open(STORAGE_FILE_PATH, 'w', encoding='utf-8') as file:
            json.dump(tuple(self.uuids), file, default=lambda uuid: uuid.hex)

    def load(self) -> None:
        if STORAGE_FILE_PATH.exists():
            with open(STORAGE_FILE_PATH, encoding='utf-8') as file:
                self.uuids = {UUID(uuid) for uuid in json.load(file)}

    def add_uuid(self, uuid: UUID) -> None:
        self.uuids.add(uuid)

    def clear(self) -> None:
        self.uuids.clear()

    def is_exist(self, uuid: UUID) -> bool:
        return uuid in self.uuids
