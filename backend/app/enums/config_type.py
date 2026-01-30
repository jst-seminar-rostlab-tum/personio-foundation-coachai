"""Enum definitions for config type."""

from enum import Enum as PyEnum


# Enum for the type column
class ConfigType(PyEnum):
    """Enum for config type."""

    int = 'int'
    string = 'string'
    boolean = 'boolean'
