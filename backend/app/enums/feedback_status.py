from enum import Enum as PyEnum


class FeedbackStatus(str, PyEnum):
    pending = 'pending'
    completed = 'completed'
    failed = 'failed'
