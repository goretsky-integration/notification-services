import abc
import json
import pathlib
import uuid

__all__ = (
    'IngredientStopSaleIDsStorage',
    'CheatedPhonesCountStorage',
)


class BaseStorage(abc.ABC):

    def __init__(self, storage_path: pathlib.Path):
        self._storage_path = storage_path
        self._data = None

    def __enter__(self):
        self.load()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.save()

    @abc.abstractmethod
    def load(self) -> None:
        pass

    @abc.abstractmethod
    def save(self) -> None:
        pass


class IngredientStopSaleIDsStorage(BaseStorage):

    def load(self) -> None:
        if not self._storage_path.exists():
            self._storage_path.write_text('[]')
        with open(self._storage_path) as file:
            self._data = {uuid.UUID(stop_sale_uuid) for stop_sale_uuid in json.load(file)}

    def save(self) -> None:
        uuids = [stop_sale_uuid.hex for stop_sale_uuid in self._data]
        with open(self._storage_path, 'w') as file:
            json.dump(uuids, file)

    def is_exist(self, stop_sale_uuid: uuid.UUID) -> bool:
        return stop_sale_uuid in self._data

    def add_uuid(self, stop_sale_uuid: uuid.UUID) -> None:
        self._data.add(stop_sale_uuid)

    def clear(self) -> None:
        self._data = set()


class CheatedPhonesCountStorage(BaseStorage):

    def load(self) -> None:
        if not self._storage_path.exists():
            self._data = {}
        else:
            with open(self._storage_path) as file:
                self._data: dict[str, int] = json.load(file)

    def save(self) -> None:
        with open(self._storage_path, 'w') as file:
            json.dump(self._data, file)

    def set(self, phone_number: str, count: int):
        self._data[phone_number] = count

    def get(self, phone_number: str) -> int:
        return self._data.get(phone_number, 0)

    def clear(self):
        self._data = {}
