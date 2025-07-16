import logging
from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlmodel import Session as DBSession
from sqlmodel import select

from app.connections.vertexai_client import call_structured_llm
from app.enums.feedback_status import FeedbackStatus
from app.enums.language import LanguageCode
from app.models.conversation_scenario import DifficultyLevel
from app.models.session_feedback import SessionFeedback
from app.models.user_profile import UserProfile
from app.schemas import ConversationScenarioCreate
from app.schemas.advisor_response import AdvisorResponse
from app.schemas.user_profile import ScenarioAdvice

mock_persona = """
                **Name**: Positive Pam
                **Personality**: Upbeat, eager to please, growth-oriented, avoids negativity
                **Behavioral Traits**:
                - Overly agreeable 
                — avoids conflict or disagreement
                - Deflects criticism with enthusiasm ("I'll fix it!")
                - Often hides stress or burnout behind optimism
                - Pushes for promotions or more responsibility before ready
                - Uses toxic positivity to dismiss serious concerns
                
                **Training Focus**:
                - Delivering constructive feedback without sugarcoating
                - Encouraging honest reflection and accountability
                - Identifying signs of masked stress or burnout
                - Setting realistic growth expectations
                - Navigating emotionally complex conversations with high performers
                
                **Company Position**: Development Coordinator (5 years experience)
"""

mock_situational_facts = """
                **Positive Performance**
                - Pam developed two successful community outreach pilots.
                - Partners often compliment Pam's creativity and energy.

                **Areas for Improvement**
                - Pam sometimes misses internal deadlines for reports and data submissions.
                - Team members report Pam can be hard to reach on short notice.

                **Review Outcome**
                - Overall rating is "Meets Expectations" — strong external impact but inconsistency 
                in internal follow-through prevented "Exceeds Expectations".
                - A standard 3% merit raise will be applied, same as most peers.

                **Organizational Context**
                - The NGO emphasizes reliability to secure renewed donor funding.
                - This review cycle is slightly stricter due to new funder accountability 
                requirements.

                **Silver Lining**
                - The manager believes Pam can reach "Exceeds Expectations" next year with more 
                consistent internal coordination.
"""


def get_mock_advisor_response() -> AdvisorResponse:
    return AdvisorResponse(
        custom_category_label='Performance Reviews',
        persona=mock_persona,
        persona_name='positive',
        situational_facts=mock_situational_facts,
        difficulty_level=DifficultyLevel.medium,
        mascot_speech='Hi! How about you try training for a Performance Review?',
    )


def get_mock_session_feedback() -> SessionFeedback:
    return SessionFeedback(
        id=uuid4(),
        session_id=uuid4(),
        scores={'structure': 4, 'empathy': 5, 'focus': 4, 'clarity': 4},
        tone_analysis={'positive': 70, 'neutral': 20, 'negative': 10},
        overall_score=4.3,
        full_audio_filename='full_audio_123.mp3',
        document_names=[
            'Teamwork: An Open Access Practical Guide',
            'Psychology of Human Relations',
        ],
        speak_time_percent=60.5,
        questions_asked=5,
        session_length_s=1800,
        goals_achieved=[
            'Bring clarity to the situation',
            'Encourage open dialogue',
            'Maintain professionalism',
        ],
        example_positive=[
            {
                'heading': 'Clear framing of the issue',
                'feedback': (
                    'You effectively communicated the specific issue (missed deadlines) and its'
                    ' impact on the team without being accusatory.'
                ),
                'quote': (
                    "I've noticed that several deadlines were missed last week, and "
                    "it's causing team to fall behind on the overall project timeline."
                ),
            }
        ],
        example_negative=[
            {
                'heading': 'Lack of specific examples',
                'feedback': (
                    "While you mentioned missed deadlines, you didn't provide specific "
                    'instances or data to illustrate the issue. Including concrete examples '
                    'would strengthen your feedback.'
                ),
                'quote': (
                    'The report due on Friday was submitted on Monday, which delayed our progress.'
                ),
                'improved_quote': (
                    'Ensure deadlines are met by setting clear expectations and providing '
                    'specific examples of missed deadlines.'
                ),
            }
        ],
        recommendations=[
            {
                'heading': 'Practice the STAR method',
                'recommendation': (
                    'When giving feedback, use the Situation, Task, Action, Result framework to'
                    ' provide more concrete examples.'
                ),
            },
            {
                'heading': 'Ask more diagnostic questions',
                'recommendation': (
                    'Spend more time understanding root causes before moving to solutions. This'
                    ' builds empathy and leads to more effective outcomes.'
                ),
            },
            {
                'heading': 'Define next steps',
                'recommendation': (
                    'End feedback conversations with agreed-upon actions to ensure clarity and '
                    'accountability.'
                ),
            },
        ],
        status=FeedbackStatus.completed,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


class AdvisorService:
    def __init__(self, db: DBSession) -> None:
        self.db = db

    def generate_and_store_advice(
        self, session_feedback: SessionFeedback, user_profile_id: UUID
    ) -> None:
        logging.info(f'Generating advice for session feedback ID: {session_feedback.id}')
        scenario_advice = self._generate_advice(session_feedback=session_feedback)
        statement = select(UserProfile).where(UserProfile.id == user_profile_id)
        user_profile = self.db.exec(statement).one_or_none()
        if user_profile is None:
            logging.error(f'User profile with ID {user_profile_id} not found.')
            return
        user_profile.scenario_advice = scenario_advice.model_dump()
        self.db.add(user_profile)
        self.db.commit()
        logging.info(f'Advice generated and stored for user profile ID: {user_profile.id}')

    def _generate_advice(self, session_feedback: SessionFeedback) -> ScenarioAdvice:
        language_code = LanguageCode.en
        try:
            previous_scenario = session_feedback.session.scenario
            language_code = session_feedback.session.scenario.language_code
        except Exception as e:
            print(f'No previous scenario for generating advice found: {e}')
            previous_scenario = None

        prompt = f"""
        Analyze the following feedback from an HR employee's conversation training session. Using
        this, generate a new conversation scenario for which you choose fittingly the welcoming
        message, conversation category, situational facts, difficulty level and persona, who the
        employee should converse with.
        Choose these attributes in a way that the employee can further develop themselves 
        and improve their weaknesses.

        ### Context
        --Feedback
        Category of previous scenario:
        {previous_scenario.category.name if previous_scenario else 'No previous scenario available'}
        Difficulty of previous scenario:
        {
            previous_scenario.difficulty_level.name
            if previous_scenario
            else ('No previous scenario available')
        }
        Employee scores (out of 5)
        {session_feedback.scores}
        Overall score (out of 5)
        {session_feedback.overall_score}
        Achieved goals:
        {' '.join(session_feedback.goals_achieved)}
        Examples of what the employee did well:
        {session_feedback.example_positive}
        Examples of what the employee did badly:
        {session_feedback.example_negative}
        Recommendations how the employee can improve:
        {session_feedback.recommendations}

        ### Instructions
        Format your output as an 'AdvisorResponse' object.
        Each live feedback item represents a Pydantic model with the following 5 fields 
        and their restrictions:
        1. custom_category_label: Category of a training scenario. Try to be concise. 
        Example: Performance Reviews, Giving Feedback
        2. persona: A description of the AI persona, who the user will train with. 
        Format it like this:
                **Name**: Positive Pam
                **Personality**: Upbeat, eager to please, growth-oriented, avoids negativity
                **Behavioral Traits**:
                - Overly agreeable 
                — avoids conflict or disagreement
                - Deflects criticism with enthusiasm ("I'll fix it!")
                - Often hides stress or burnout behind optimism
                - Pushes for promotions or more responsibility before ready
                - Uses toxic positivity to dismiss serious concerns

                **Training Focus**:
                - Delivering constructive feedback without sugarcoating
                - Encouraging honest reflection and accountability
                - Identifying signs of masked stress or burnout
                - Setting realistic growth expectations
                - Navigating emotionally complex conversations with high performers

                **Company Position**: Development Coordinator (5 years experience)
        3. persona_name: Name of the AI persona, who the user will train with.
        Example: Positive Pam, Casual Candice, etc.
        4. situational_facts: Context of the training scenario:
        5. difficulty_level: How difficult the conversation should be. 
        Choose one of those options: 'easy', 'medium', 'hard'
        6. mascot_speech: 1-2 sentences that encourage the user to try training with the scenario 
        you generate. Try to keep the sentences short
        Example for mascot_speech if previous scenario level was 'Conflict Resolution' on 'easy': 
        I saw you did good with easy Conflict Resolution, how about you try medium 
        Conflict Resolution?
        Example for mascot_speech if an examples of what the employee did badly in 
        'Performance Reviews' is 'Being vague: You were previously a bit vague in your training,
         how about you try Performance Reviews again?

        Do not include markdown, explanation, or code formatting.
        """

        advisor_response = call_structured_llm(
            system_prompt='You are an expert communication coach analyzing previous feedback '
            f'and training scenario. Always respond in {language_code} language using the'
            ' specified output model format.',
            request_prompt=prompt,
            output_model=AdvisorResponse,
            mock_response=get_mock_advisor_response(),
        )

        new_conversation_scenario = ConversationScenarioCreate(
            category_id=None,
            custom_category_label=advisor_response.custom_category_label,
            persona_name=advisor_response.persona_name,
            persona=advisor_response.persona,
            situational_facts=advisor_response.situational_facts,
            difficulty_level=DifficultyLevel(advisor_response.difficulty_level),
            language_code=language_code,
        )

        return ScenarioAdvice(
            mascot_speech=advisor_response.mascot_speech, scenario=new_conversation_scenario
        )


if __name__ == '__main__':
    # Example usage/Testing
    test_session_feedback = get_mock_session_feedback()

    advice_service = AdvisorService()

    scenario, mascot_speech = advice_service.generate_advice(session_feedback=test_session_feedback)
    print('Mascot speech:', mascot_speech)
    print('scenario.category_id:', scenario.category_id)
    print('scenario.custom_category_label:', scenario.custom_category_label)
    print('scenario.persona:', scenario.persona)
    print('scenario.difficulty_level:', scenario.difficulty_level)
    print('scenario.language_code:', scenario.language_code)
