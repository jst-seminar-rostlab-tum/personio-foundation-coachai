from enum import Enum as PyEnum


class ScenarioPreparationStatus(str, PyEnum):
    pending = 'pending'
    completed = 'completed'
    failed = 'failed'
