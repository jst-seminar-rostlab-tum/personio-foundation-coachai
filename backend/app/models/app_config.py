from enum import Enum as PyEnum

from sqlmodel import Column, Enum, Field

from app.models.camel_case import CamelModel


# Enum for the type column
class ConfigType(PyEnum):
    int = 'int'
    string = 'string'
    boolean = 'boolean'


class AppConfig(CamelModel, table=True):
    key: str = Field(primary_key=True)
    value: str = Field(nullable=False)
    type: ConfigType = Field(sa_column=Column(Enum(ConfigType)))
