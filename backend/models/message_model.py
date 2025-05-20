
from sqlmodel import SQLModel, Field
from datetime import datetime


class MessageModel(SQLModel, table=True):  # `table=True` makes it a database table
    id: int = Field(default=None, primary_key=True)
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
