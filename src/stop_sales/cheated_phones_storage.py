import json
import pathlib

__all__ = (
    'CheatedPhonesStorage',
)

STORAGE_FILE_PATH = pathlib.Path.joinpath(
    pathlib.Path(__file__).parent.parent.parent,
    'local_storage',
    'cheated_phones.json',
)


class CheatedPhonesStorage:

    def __init__(self):
        self.phone_numbers_to_count = dict()
        self.load()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.save()

    def flush(self) -> None:
        self.save()
        self.load()

    def save(self) -> None:
        with open(STORAGE_FILE_PATH, 'w', encoding='utf-8') as file:
            json.dump(self.phone_numbers_to_count, file)

    def load(self) -> None:
        if STORAGE_FILE_PATH.exists():
            with open(STORAGE_FILE_PATH, encoding='utf-8') as file:
                self.phone_numbers_to_count = json.load(file)

    def set_count(self, phone_number: str, count: int) -> None:
        self.phone_numbers_to_count[phone_number] = count

    def get_count(self, phone_number: str) -> int:
        return self.phone_numbers_to_count.get(phone_number, 0)

    def clear(self) -> None:
        self.phone_numbers_to_count.clear()
