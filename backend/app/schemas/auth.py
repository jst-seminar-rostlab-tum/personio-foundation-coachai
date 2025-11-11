from app.models.camel_case import CamelModel


class UserCreate(CamelModel):
    full_name: str
    phone: str
    email: str
    password: str
    is_nonprofit: bool
    organization_name: str | None = None
    # code: str


class VerificationCodeCreate(CamelModel):
    phone_number: str


class VerificationCodeConfirm(CamelModel):
    phone_number: str
    code: str


class CheckUniqueRequest(CamelModel):
    email: str
    phone: str
