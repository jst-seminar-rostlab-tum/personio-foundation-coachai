from enum import Enum as PyEnum


class SessionStatus(str, PyEnum):
    started = 'started'
    completed = 'completed'
    failed = 'failed'
