from app.models.camel_case import CamelModel


class LiveFeedback(CamelModel):
    heading: str
    feedback_text: str
