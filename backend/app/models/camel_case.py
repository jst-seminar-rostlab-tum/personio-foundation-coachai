from sqlmodel import SQLModel


def to_camel(string: str) -> str:
    parts = string.split('_')
    return parts[0] + ''.join(word.capitalize() for word in parts[1:])


class CamelModel(SQLModel):
    class Config:  # type: ignore
        alias_generator = to_camel
        validate_by_name = True
