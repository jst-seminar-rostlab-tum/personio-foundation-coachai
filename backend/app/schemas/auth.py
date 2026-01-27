"""Pydantic schema definitions for auth."""

from app.models.camel_case import CamelModel


class UserCreate(CamelModel):
    """Schema for user create."""

    full_name: str
    phone: str
    email: str
    password: str
    organization_name: str | None = None
    # code: str


class VerificationCodeCreate(CamelModel):
    """Schema for verification code create."""

    phone_number: str


class VerificationCodeConfirm(CamelModel):
    """Schema for verification code confirm."""

    phone_number: str
    code: str


class CheckUniqueRequest(CamelModel):
    """Schema for check unique request."""

    email: str
    phone: str
