import pathlib

from services.storages import PhoneNumbersStorage


def main():
    storage_file_path = pathlib.Path.joinpath(pathlib.Path(__file__).parent.parent, 'local_storage', 'phone_numbers.db')
    with PhoneNumbersStorage(storage_file_path) as storage:
        storage.clear_all()


if __name__ == '__main__':
    main()
