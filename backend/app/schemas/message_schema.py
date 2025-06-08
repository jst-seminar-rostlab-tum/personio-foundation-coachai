from datetime import datetime

from app.models.camel_case import CamelModel


class MessageBaseSchema(CamelModel):
    content: str


class MessageCreateSchema(MessageBaseSchema):
    pass


class MessageSchema(MessageBaseSchema):
    id: int
    created_at: datetime

    model_config = {
        'from_attributes': True,
    }
