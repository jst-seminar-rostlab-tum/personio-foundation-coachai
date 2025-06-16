from pydantic import BaseModel


class MockUser(BaseModel):
    email: str
    password: str
    phone: str
    full_name: str
