import unittest
from uuid import uuid4

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from app.models.conversation_scenario import ConversationScenario, ConversationScenarioCreate
from app.services.conversation_scenario_service import create_conversation_scenario


class TestCreateConversationScenario(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        # initial setup for the db
        cls.engine = create_engine('sqlite:///:memory:', echo=False)
        cls.Session = sessionmaker(bind=cls.engine)
        SQLModel.metadata.create_all(bind=cls.engine)

    def setUp(self) -> None:
        # create a new session for each test
        self.session = self.Session()

    def tearDown(self) -> None:
        # close the session after each test
        self.session.close()

    def test_create_conversation_scenario(self) -> None:
        # prepare test data
        conversation_scenario_data = ConversationScenarioCreate(
            category_id=uuid4(),
            user_id='f5957372-7607-4628-be88-661896bd9eb7',
            custom_category_label='Custom Category',
            goal='Test Goal',
            other_party='Test Other Party',
            difficulty_id='d1b2c3f4-5678-90ab-cdef-1234567890ab',
            tone='Friendly',
            complexity='Medium',
            status='draft',
            context='Test Context',
        )

        created = create_conversation_scenario(conversation_scenario_data, self.session)

        db_obj = self.session.get(ConversationScenario, created.id)
        self.assertIsNotNone(db_obj)
        self.assertEqual(db_obj.category_id, conversation_scenario_data.category_id)
        self.assertEqual(db_obj.user_id, conversation_scenario_data.user_id)
        self.assertEqual(
            db_obj.custom_category_label, conversation_scenario_data.custom_category_label
        )
        self.assertEqual(db_obj.goal, conversation_scenario_data.goal)
        self.assertEqual(db_obj.other_party, conversation_scenario_data.other_party)
        self.assertEqual(db_obj.difficulty_id, conversation_scenario_data.difficulty_id)
        self.assertEqual(db_obj.tone, conversation_scenario_data.tone)
        self.assertEqual(db_obj.complexity, conversation_scenario_data.complexity)
        self.assertEqual(db_obj.status, conversation_scenario_data.status)
        self.assertEqual(db_obj.context, conversation_scenario_data.context)


if __name__ == '__main__':
    unittest.main()
