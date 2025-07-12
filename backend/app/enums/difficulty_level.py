from enum import Enum as PyEnum


class DifficultyLevel(str, PyEnum):
    easy = 'easy'
    medium = 'medium'
    hard = 'hard'
