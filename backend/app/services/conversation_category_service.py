"""Service layer for conversation category service."""

from sqlmodel import Session as DBSession
from sqlmodel import select

from app.models.conversation_category import ConversationCategory
from app.schemas.conversation_category import ConversationCategoryRead


class ConversationCategoryService:
    """Service for retrieving conversation categories."""

    def __init__(self, db: DBSession) -> None:
        """Initialize the service with a database session.

        Parameters:
            db (DBSession): Database session used for queries.
        """
        self.db = db

    def fetch_all_conversation_categories(self) -> list[ConversationCategoryRead]:
        """Retrieve all conversation categories.

        Returns:
            list[ConversationCategoryRead]: Categories from the database.
        """
        statement = select(ConversationCategory)
        categories = self.db.exec(statement).all()
        return [ConversationCategoryRead(**category.model_dump()) for category in categories]
