from sqlmodel import Session as DBSession
from sqlmodel import select

from app.models.conversation_category import ConversationCategory
from app.schemas.conversation_category import ConversationCategoryRead


class ConversationCategoryService:
    def __init__(self, db: DBSession) -> None:
        self.db = db

    def fetch_all_conversation_categories(self) -> list[ConversationCategoryRead]:
        """
        Retrieve all conversation categories.
        """
        statement = select(ConversationCategory)
        categories = self.db.exec(statement).all()
        return [ConversationCategoryRead.from_orm(category) for category in categories]
