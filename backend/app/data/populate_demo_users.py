from app.data import create_mock_users, delete_mock_users


def populate_demo_users() -> None:
    print('Removing mock users...')
    delete_mock_users()

    print('Creating mock users...')
    create_mock_users()


if __name__ == '__main__':
    populate_demo_users()
