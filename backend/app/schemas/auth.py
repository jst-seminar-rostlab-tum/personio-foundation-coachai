from app.models.camel_case import CamelModel


class CreateUserRequest(CamelModel):
    full_name: str
    phone: str
    email: str
    password: str
    # code: str


class SendVerificationRequest(CamelModel):
    phone_number: str


class VerifyCodeRequest(CamelModel):
    phone_number: str
    code: str
