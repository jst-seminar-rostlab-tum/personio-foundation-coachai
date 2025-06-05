from enum import Enum as PyEnum
from typing import Optional

from sqlalchemy import Column
from sqlalchemy import Enum as SQLEnum
from sqlmodel import Field

from app.models.base import BaseModel


# Enum for the type column
class ConfigType(PyEnum):
    int = 'int'
    string = 'string'
    boolean = 'boolean'


# Main AppConfig model
class AppConfig(BaseModel, table=True):
    key: str = Field(primary_key=True)
    value: str = Field(nullable=False)
    type: ConfigType = Field(sa_column=Column(SQLEnum(ConfigType)))


# Schema for creating a new AppConfig
class AppConfigCreate(BaseModel):
    key: str
    value: str
    type: Optional[ConfigType] = None


# Schema for reading AppConfig data
class AppConfigRead(BaseModel):
    key: str
    value: str
    type: ConfigType
