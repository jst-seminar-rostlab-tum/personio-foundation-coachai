from datetime import datetime

from sqlmodel import Field, SQLModel


class MessageModel(SQLModel, table=True):  # `table=True` makes it a database table
    id: int = Field(default=None, primary_key=True)
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
