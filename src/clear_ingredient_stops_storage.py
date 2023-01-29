import pathlib

from services.storages import ObjectUUIDStorage


def main():
    storage_file_path = pathlib.Path.joinpath(pathlib.Path(__file__).parent.parent, 'local_storage',
                                              'daily_ingredient_stops.db')
    with ObjectUUIDStorage(storage_file_path) as storage:
        storage.clear_all()


if __name__ == '__main__':
    main()
