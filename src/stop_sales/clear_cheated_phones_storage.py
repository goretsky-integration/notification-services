from cheated_phones_storage import CheatedPhonesStorage


def main():
    with CheatedPhonesStorage() as storage:
        storage.clear()


if __name__ == '__main__':
    main()
