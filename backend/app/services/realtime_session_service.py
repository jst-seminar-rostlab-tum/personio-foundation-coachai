from sqlmodel import Session as DBSession


class RealtimeSessionService:
    def __init__(self, db: DBSession) -> None:
        self.db = db

    pass
