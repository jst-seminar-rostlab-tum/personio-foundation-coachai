"""Enum definitions for account role."""

from enum import Enum as PyEnum


class AccountRole(str, PyEnum):
    """Enum for account role."""

    user = 'user'
    admin = 'admin'
