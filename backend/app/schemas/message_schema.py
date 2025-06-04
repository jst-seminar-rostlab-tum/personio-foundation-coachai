from datetime import datetime

from pydantic import BaseModel


class MessageBaseSchema(BaseModel):
    content: str


class MessageCreateSchema(MessageBaseSchema):
    pass


class MessageSchema(MessageBaseSchema):
    id: int
    created_at: datetime

    model_config = {
        'from_attributes': True,
    }
