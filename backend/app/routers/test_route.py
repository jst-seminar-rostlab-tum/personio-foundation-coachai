from uuid import UUID, uuid4

from fastapi import APIRouter

from app.models.base import BaseModel, Field

router = APIRouter()


class TestModel(BaseModel):
    first_name: str = Field(alias='firstName')
    last_name: str = Field(alias='lastName')
    user_id: UUID = Field(default_factory=uuid4, alias='userId')
    created_at: str = Field(alias='createdAt')


@router.post('/test-camel', response_model=TestModel)
async def test_camel_case(test_data: TestModel) -> TestModel:
    # This will print the internal snake_case representation
    print('Internal representation:', test_data.model_dump())
    # This will return the camelCase representation
    return test_data


@router.get('/test-camel', response_model=TestModel)
async def get_test_camel() -> TestModel:
    # Create a test instance with snake_case
    test_data = TestModel(first_name='John', last_name='Doe', created_at='2024-03-20')
    # This will automatically convert to camelCase in the response
    return test_data
