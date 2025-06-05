from sqlmodel import Field

from app.models.base import BaseModel


class Language(BaseModel, table=True):  # `table=True` makes it a database table
    code: str = Field(default=None, primary_key=True)
    name: str


# Schema for creating a new Language
class LanguageCreate(BaseModel):
    code: str
    name: str


# Schema for reading Language data
class LanguageRead(BaseModel):
    code: str
    name: str
