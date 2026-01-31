"""Database model definitions for app config."""

from sqlmodel import Column, Enum, Field

from app.enums.config_type import ConfigType
from app.models.camel_case import CamelModel


class AppConfig(CamelModel, table=True):
    """Database model for app config."""

    key: str = Field(primary_key=True)
    value: str = Field(nullable=False)
    type: ConfigType = Field(sa_column=Column(Enum(ConfigType)))
