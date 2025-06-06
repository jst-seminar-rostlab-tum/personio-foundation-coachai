from typing import TYPE_CHECKING

from sqlmodel import Field

from app.models.camel_case import CamelModel

if TYPE_CHECKING:
    pass


class Language(CamelModel, table=True):  # `table=True` makes it a database table
    code: str = Field(default=None, primary_key=True)
    name: str


# Schema for creating a new Language
class LanguageCreate(CamelModel):
    code: str
    name: str


# Schema for reading Language data
class LanguageRead(CamelModel):
    code: str
    name: str
