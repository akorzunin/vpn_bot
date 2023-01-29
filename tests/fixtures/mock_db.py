from tests.mock_data import mock_db


def replace_db(crud):
    crud.users = mock_db.mock_users
    crud.payments = mock_db.mock_payments


if __name__ == "__main__":
    from src.db import crud

    replace_db(crud)
