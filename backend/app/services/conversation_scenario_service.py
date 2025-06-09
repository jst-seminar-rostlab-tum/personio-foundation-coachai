from sqlmodel import Session as DBSession

from app.models.conversation_scenario import ConversationScenario, ConversationScenarioCreate


def create_conversation_scenario(
    conversation_scenario_data: ConversationScenarioCreate, db_session: DBSession
) -> ConversationScenario:
    """
    Create ConversationScenario
    """
    new_conversation_scenario = ConversationScenario(**conversation_scenario_data.model_dump())
    db_session.add(new_conversation_scenario)
    db_session.commit()
    db_session.refresh(new_conversation_scenario)
    return new_conversation_scenario
