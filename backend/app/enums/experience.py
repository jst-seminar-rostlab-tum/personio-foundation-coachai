from enum import Enum as PyEnum


class Experience(str, PyEnum):
    beginner = 'beginner'
    intermediate = 'intermediate'
    skilled = 'skilled'
    advanced = 'advanced'
    expert = 'expert'
