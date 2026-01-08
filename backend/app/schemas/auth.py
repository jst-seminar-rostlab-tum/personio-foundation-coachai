from app.models.camel_case import CamelModel


class UserCreate(CamelModel):
    full_name: str
    phone: str
    verification_code: str
    email: str
    password: str
    organization_name: str | None = None


class VerificationCodeCreate(CamelModel):
    phone_number: str


class CheckUniqueRequest(CamelModel):
    email: str
    phone: str
