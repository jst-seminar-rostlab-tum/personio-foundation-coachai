from enum import Enum
from uuid import UUID


class MockUserIdsEnum(Enum):
    """
    Enum for mock user IDs to be used in dummy data generation.
    This enum is used to ensure that the IDs are consistent across
    different parts of the application.
    """

    USER = UUID('3a9a8970-afbe-4ee1-bc11-9dcad7875ddf')
    ADMIN = UUID('763c76f3-e5a4-479c-8b53-e3418d5e2ef5')
