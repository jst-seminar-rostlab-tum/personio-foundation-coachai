"""Interface helpers for mock user."""

from pydantic import BaseModel


class MockUser(BaseModel):
    """Mock user credentials for demo and testing flows.

    Parameters:
        email (str): User email address.
        password (str): User password.
        phone (str): User phone number.
        full_name (str): Full display name.
    """

    email: str
    password: str
    phone: str
    full_name: str
