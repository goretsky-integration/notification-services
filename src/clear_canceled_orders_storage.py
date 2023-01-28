import pathlib

from services.storages import CanceledOrdersStorage


def main():
    storage_file_path = pathlib.Path.joinpath(pathlib.Path(__file__).parent.parent, 'local_storage', 'canceled_orders.db')
    with CanceledOrdersStorage(storage_file_path) as storage:
        storage.clear_all()


if __name__ == '__main__':
    main()
