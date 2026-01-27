"""Pydantic schema definitions for app config."""

from app.enums.config_type import ConfigType
from app.models.camel_case import CamelModel


# Schema for creating a new AppConfig
class AppConfigCreate(CamelModel):
    """Schema for app config create."""

    key: str
    value: str
    type: ConfigType


# Schema for reading AppConfig data
class AppConfigRead(CamelModel):
    """Schema for app config read."""

    key: str
    value: str
    type: ConfigType
