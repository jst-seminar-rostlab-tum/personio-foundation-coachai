from enum import Enum as PyEnum

from sqlmodel import Column, Enum, Field

from app.models.camel_case import CamelModel


# Enum for the type column
class ConfigType(PyEnum):
    int = 'int'
    string = 'string'
    boolean = 'boolean'


# Main AppConfig model
class AppConfig(CamelModel, table=True):
    key: str = Field(primary_key=True)
    value: str = Field(nullable=False)
    type: ConfigType = Field(sa_column=Column(Enum(ConfigType)))


# Schema for creating a new AppConfig
class AppConfigCreate(CamelModel):
    key: str
    value: str
    type: ConfigType | None = None


# Schema for reading AppConfig data
class AppConfigRead(CamelModel):
    key: str
    value: str
    type: ConfigType
