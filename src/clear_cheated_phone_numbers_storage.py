import pathlib

from storages import CheatedPhonesCountStorage


def main():
    storage_path = pathlib.Path.joinpath(pathlib.Path(__file__).parent.parent, 'local_storage', 'cheated_phones.json')
    with CheatedPhonesCountStorage(storage_path) as storage:
        storage.clear()


if __name__ == '__main__':
    main()
