from app.models.camel_case import CamelModel


class AdvisorResponse(CamelModel):
    custom_category_label: str
    persona: str
    situational_facts: str
    difficulty_level: str

    mascot_speech: str
