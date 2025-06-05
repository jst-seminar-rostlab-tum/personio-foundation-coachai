from typing import Any, TypedDict, TypeVar, Union

from pydantic import ConfigDict
from sqlmodel import Field, SQLModel

T = TypeVar('T', bound='BaseModel')


class ModelDumpKwargs(TypedDict, total=False):
    exclude_none: bool
    exclude_defaults: bool
    exclude_unset: bool
    by_alias: bool


class BaseModel(SQLModel):
    """Base model that handles camelCase/snake_case conversion for API requests/responses."""

    model_config = ConfigDict(
        alias_generator=lambda x: ''.join(['_' + c.lower() if c.isupper() else c for c in x]),
        populate_by_name=True,
        from_attributes=True,
    )

    @classmethod
    def from_orm(cls: type[T], obj: Union[dict, SQLModel]) -> T:
        """Convert snake_case to camelCase when creating from ORM."""
        if not isinstance(obj, dict):
            obj = obj.__dict__
        return cls.model_validate(obj)

    def model_dump(self, **kwargs: ModelDumpKwargs) -> dict[str, Any]:
        """Convert camelCase to snake_case when serializing."""
        return super().model_dump(by_alias=True, **kwargs)


__all__ = ['BaseModel', 'Field']
