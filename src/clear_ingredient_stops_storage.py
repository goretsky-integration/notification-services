import pathlib

from storages import IngredientStopSaleIDsStorage


def main():
    storage_path = pathlib.Path.joinpath(pathlib.Path(__file__).parent.parent, 'local_storage', 'ingredient_stops.json')
    with IngredientStopSaleIDsStorage(storage_path) as storage:
        storage.clear()


if __name__ == '__main__':
    main()
