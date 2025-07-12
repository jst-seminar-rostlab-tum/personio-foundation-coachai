from app.enums.config_type import ConfigType
from app.models.camel_case import CamelModel


# Schema for creating a new AppConfig
class AppConfigCreate(CamelModel):
    key: str
    value: str
    type: ConfigType


# Schema for reading AppConfig data
class AppConfigRead(CamelModel):
    key: str
    value: str
    type: ConfigType
