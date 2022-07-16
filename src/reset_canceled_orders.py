import db


def main():
    shift_manager_accounts = db.get_shift_manager_accounts()
    for account_name in shift_manager_accounts:
        storage = db.CanceledOrderUUIDsStorage(account_name)
        storage.clear()


if __name__ == '__main__':
    main()
