"""Database model definitions for camel case.
For frontend compatibility
"""

from sqlmodel import SQLModel


def to_camel(string: str) -> str:
    """Convert a snake_case string to lowerCamelCase.

    Parameters:
        string (str): Input string in snake_case.

    Returns:
        str: Converted lowerCamelCase string.
    """
    parts = string.split('_')
    return parts[0] + ''.join(word.capitalize() for word in parts[1:])


class CamelModel(SQLModel):
    """Database model for camel model."""

    class Config:  # type: ignore
        alias_generator = to_camel
        validate_by_name = True
