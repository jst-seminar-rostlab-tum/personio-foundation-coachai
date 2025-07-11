from enum import Enum as PyEnum


# Enum for the type column
class ConfigType(PyEnum):
    int = 'int'
    string = 'string'
    boolean = 'boolean'
