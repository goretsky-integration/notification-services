from storage import UUIDStorage


def main():
    with UUIDStorage() as uuid_storage:
        uuid_storage.clear()


if __name__ == '__main__':
    main()
