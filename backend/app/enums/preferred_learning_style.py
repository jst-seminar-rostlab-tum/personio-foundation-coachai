from enum import Enum as PyEnum


class PreferredLearningStyle(str, PyEnum):
    visual = 'visual'
    auditory = 'auditory'
    kinesthetic = 'kinesthetic'
