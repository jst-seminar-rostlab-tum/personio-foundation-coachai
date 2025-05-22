from sqlmodel import Field, SQLModel


class Language(SQLModel, table=True):  # `table=True` makes it a database table
    code: str = Field(default=None, primary_key=True)
    name : str
# Schema for creating a new Language
class LanguageCreate(SQLModel):
    code: str
    name: str
# Schema for reading Language data
class LanguageRead(SQLModel):
    code: str
    name: str
