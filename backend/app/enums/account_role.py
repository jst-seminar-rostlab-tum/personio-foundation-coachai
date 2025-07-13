from enum import Enum as PyEnum


class AccountRole(str, PyEnum):
    user = 'user'
    admin = 'admin'
