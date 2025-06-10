from datetime import UTC, datetime
from uuid import uuid4

from app.models.app_config import AppConfig, ConfigType
from app.models.confidence_area import ConfidenceArea
from app.models.conversation_category import ConversationCategory
from app.models.conversation_scenario import ConversationScenario, ConversationScenarioStatus
from app.models.difficulty_level import DifficultyLevel  # Assuming this is the new model
from app.models.experience import Experience
from app.models.goal import Goal
from app.models.language import Language  # Import the Language model
from app.models.learning_style import LearningStyle
from app.models.rating import Rating
from app.models.review import Review
from app.models.scenario_preparation import ScenarioPreparation, ScenarioPreparationStatus
from app.models.session import Session
from app.models.session_feedback import (
    FeedbackStatusEnum,
    SessionFeedback,
)
from app.models.session_turn import SessionTurn, SpeakerEnum
from app.models.user_confidence_score import UserConfidenceScore
from app.models.user_goal import UserGoal
from app.models.user_profile import UserProfile, UserRole


def get_dummy_learning_styles() -> list[LearningStyle]:
    """
    Generate dummy LearningStyle data.
    """
    return [
        LearningStyle(
            id=uuid4(),
            label='Visual',
            description='Prefers learning through visual aids like diagrams and charts.',
        ),
        LearningStyle(
            id=uuid4(),
            label='Auditory',
            description='Prefers learning through listening to explanations and discussions.',
        ),
        LearningStyle(
            id=uuid4(),
            label='Kinesthetic',
            description='Prefers learning through hands-on activities and physical engagement.',
        ),
    ]


def get_dummy_languages() -> list[Language]:
    return [
        Language(code='en', name='English'),
        Language(code='de', name='German'),
    ]


def get_dummy_experiences() -> list[Experience]:
    return [
        Experience(id=uuid4(), label='Beginner', description='New to the field'),
        Experience(id=uuid4(), label='Intermediate', description='Some experience'),
        Experience(id=uuid4(), label='Expert', description='Highly experienced'),
    ]


def get_dummy_goals() -> list[Goal]:
    return [
        Goal(
            id=uuid4(),
            label='Improve Communication',
            description='Focus on verbal and non-verbal communication skills.',
        ),
        Goal(
            id=uuid4(),
            label='Time Management',
            description='Improve productivity and manage time effectively.',
        ),
    ]


def get_dummy_difficulty_levels() -> list[DifficultyLevel]:
    return [
        DifficultyLevel(id=uuid4(), label='Easy'),
        DifficultyLevel(id=uuid4(), label='Medium'),
        DifficultyLevel(id=uuid4(), label='Hard'),
    ]


def get_dummy_user_profiles(
    experiences: list[Experience],
    learning_styles: list[LearningStyle],
) -> list[UserProfile]:
    """
    Generate dummy UserProfile data.
    """
    return [
        UserProfile(
            id=uuid4(),
            preferred_language='en',
            role=UserRole.user,
            experience_id=experiences[0].id,
            preferred_learning_style_id=learning_styles[0].id,
            store_conversations=False,
            total_sessions=32,
            training_time=4.5,
            current_streak_days=3,
            average_score=82,
            goals_achieved=4,
        ),
        UserProfile(
            id=uuid4(),
            preferred_language='de',
            role=UserRole.admin,
            experience_id=experiences[1].id,
            preferred_learning_style_id=learning_styles[1].id,
            store_conversations=True,
            total_sessions=5,
            training_time=4.2,
            current_streak_days=2,
            average_score=87,
            goals_achieved=2,
        ),
    ]


def get_dummy_user_goals(user_profiles: list[UserProfile], goals: list[Goal]) -> list[UserGoal]:
    return [
        UserGoal(goal_id=goals[0].id, user_id=user_profiles[0].id),
        UserGoal(goal_id=goals[1].id, user_id=user_profiles[1].id),
    ]


def get_dummy_reviews(user_profiles: list[UserProfile], sessions: list[Session]) -> list[Review]:
    return [
        Review(
            id=uuid4(),
            user_id=user_profiles[0].id,
            session_id=sessions[0].id,  # Link to the first session
            rating=5,
            comment='Excellent service!',
        ),
        Review(
            id=uuid4(),
            user_id=user_profiles[1].id,
            session_id=sessions[1].id,  # Link to a second session
            rating=2,
            comment='I found the sessions a bit too fast-paced.',
        ),
        Review(
            id=uuid4(),
            user_id=user_profiles[0].id,
            rating=4,
            comment='Good overall, but could use more examples.',
        ),
    ]


def get_dummy_conversation_scenarios(
    user_profiles: list[UserProfile], difficulty_levels: list[DifficultyLevel]
) -> list[ConversationScenario]:
    return [
        ConversationScenario(
            id=uuid4(),
            user_id=user_profiles[0].id,
            category_id=None,
            custom_category_label='Custom Category 1',
            context='Context 1',
            goal='Goal 1',
            other_party='Other Party 1',
            difficulty_id=difficulty_levels[0].id,
            tone='Friendly',
            complexity='Low',
            status=ConversationScenarioStatus.draft,  # Use the enum instead of a string
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        ),
        ConversationScenario(
            id=uuid4(),
            user_id=user_profiles[1].id,
            category_id=None,
            custom_category_label='Custom Category 2',
            context='Context 2',
            goal='Goal 2',
            other_party='Other Party 2',
            difficulty_id=difficulty_levels[1].id,
            tone='Professional',
            complexity='Medium',
            status=ConversationScenarioStatus.draft,  # Use the enum instead of a string
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        ),
    ]


def get_dummy_ratings(
    sessions: list[Session], conversation_scenarios: list[ConversationScenario]
) -> list[Rating]:
    # Create a mapping of scenario_id to user_id from the conversation_scenarios
    scenario_to_user_map = {scenario.id: scenario.user_id for scenario in conversation_scenarios}

    return [
        Rating(
            id=uuid4(),
            session_id=sessions[0].id,  # Link to the first session
            user_id=scenario_to_user_map[
                sessions[0].scenario_id
            ],  # Get user_id from the conversation scenario
            score=5,
            comment='Excellent session!',
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        ),
        Rating(
            id=uuid4(),
            session_id=sessions[1].id,  # Link to the second session
            user_id=scenario_to_user_map[
                sessions[1].scenario_id
            ],  # Get user_id from the conversation scenario
            score=4,
            comment='Good session, but room for improvement.',
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        ),
    ]


def get_dummy_conversation_categories() -> list[ConversationCategory]:
    return [
        ConversationCategory(
            id=uuid4(),
            name='Giving Feedback',
            icon_uri='/icons/giving_feedback.svg',
            system_prompt='You are an expert in providing constructive feedback.',
            initial_prompt='What feedback challenge are you facing?',
            ai_setup={'type': 'feedback', 'complexity': 'medium'},
            default_context='One-on-one meeting with a team member.',
            default_goal='Provide constructive feedback effectively.',
            default_other_party='Team member',
            is_custom=False,
            language_code='en',
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        ),
        ConversationCategory(
            id=uuid4(),
            name='Performance Reviews',
            icon_uri='/icons/performance_reviews.svg',
            system_prompt='You are a manager conducting performance reviews.',
            initial_prompt='What aspect of performance would you like to discuss?',
            ai_setup={'type': 'review', 'complexity': 'high'},
            default_context='Formal performance review meeting.',
            default_goal='Evaluate and discuss employee performance.',
            default_other_party='Employee',
            is_custom=False,
            language_code='en',
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        ),
        ConversationCategory(
            id=uuid4(),
            name='Conflict Resolution',
            icon_uri='/icons/conflict_resolution.svg',
            system_prompt='You are a mediator resolving conflicts.',
            initial_prompt='What conflict are you trying to resolve?',
            ai_setup={'type': 'mediation', 'complexity': 'high'},
            default_context='Conflict resolution meeting between team members.',
            default_goal='Resolve conflicts and improve team dynamics.',
            default_other_party='Team members',
            is_custom=False,
            language_code='en',
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        ),
        ConversationCategory(
            id=uuid4(),
            name='Salary Discussions',
            icon_uri='/icons/salary_discussions.svg',
            system_prompt='You are a negotiator discussing salary expectations.',
            initial_prompt='What salary-related topic would you like to address?',
            ai_setup={'type': 'negotiation', 'complexity': 'medium'},
            default_context='Salary negotiation meeting.',
            default_goal='Reach a mutually beneficial agreement on salary.',
            default_other_party='Employer',
            is_custom=False,
            language_code='en',
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        ),
        ConversationCategory(
            id=uuid4(),
            name='Custom Category',
            icon_uri='/icons/custom-category.svg',
            system_prompt='',
            initial_prompt='',
            ai_setup={},
            default_context='',
            default_goal='',
            default_other_party='',
            is_custom=True,
            language_code='en',
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        ),
    ]


def get_dummy_session_turns(
    sessions: list[Session],
) -> list[SessionTurn]:
    return [
        SessionTurn(
            id=uuid4(),
            session_id=sessions[0].id,  # Link to the first session
            speaker=SpeakerEnum.user,  # Use the SpeakerEnum for the speaker
            start_offset_ms=0,
            end_offset_ms=5000,
            text='Hello, how can I help you?',
            audio_uri='https://example.com/audio/user_hello.mp3',
            ai_emotion='neutral',
            created_at=datetime.now(UTC),
        ),
        SessionTurn(
            id=uuid4(),
            session_id=sessions[1].id,  # Link to the second session
            speaker=SpeakerEnum.ai,  # Use the SpeakerEnum for the speaker
            start_offset_ms=5000,
            end_offset_ms=10000,
            text='I need assistance with my account.',
            audio_uri='https://example.com/audio/system_assistance.mp3',
            ai_emotion='concerned',
            created_at=datetime.now(UTC),
        ),
    ]


def get_dummy_sessions(conversation_scenarios: list[ConversationScenario]) -> list[Session]:
    return [
        Session(
            id=uuid4(),
            scenario_id=conversation_scenarios[0].id,
            scheduled_at=datetime.now(UTC),
            started_at=datetime.now(UTC),
            ended_at=datetime.now(UTC),
            language_code='en',  # Assuming "en" is a valid language code in the LanguageModel table
            ai_persona={'persona_name': 'AI Assistant', 'persona_role': 'Helper'},
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        ),
        Session(
            id=uuid4(),
            scenario_id=conversation_scenarios[1].id,
            scheduled_at=datetime.now(UTC),
            started_at=datetime.now(UTC),
            ended_at=datetime.now(UTC),
            language_code='de',  # Assuming "fr" is a valid language code in the LanguageModel table
            ai_persona={'persona_name': 'AI Mentor', 'persona_role': 'Guide'},
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        ),
    ]


def get_dummy_session_feedback(
    sessions: list[Session],
) -> list[SessionFeedback]:
    return [
        SessionFeedback(
            id=uuid4(),
            session_id=sessions[0].id,  # Link to the first session
            scores={'structure': 82, 'empathy': 85, 'focus': 84, 'clarity': 83},
            tone_analysis={'positive': 70, 'neutral': 20, 'negative': 10},
            overall_score=85,
            transcript_uri='https://example.com/transcripts/session1.txt',
            speak_time_percent=60.5,
            questions_asked=5,
            session_length_s=1800,
            goals_achieved=3,
            example_positive=[
                {
                    'heading': 'Clear framing of the issue',
                    'feedback': (
                        'You effectively communicated the specific issue (missed deadlines) and its'
                        ' impact on the team without being accusatory.'
                    ),
                    'quote': (
                        'I’ve noticed that several deadlines were missed last week, and '
                        'it’s causing team to fall behind on the overall project timeline.'
                    ),
                }
            ],
            example_negative=[
                {
                    'heading': 'Lack of specific examples',
                    'feedback': (
                        'While you mentioned missed deadlines, you didn’t provide specific '
                        'instances or data to illustrate the issue. Including concrete examples '
                        'would strengthen your feedback.'
                    ),
                    'quote': (
                        'The report due on Friday was submitted on Monday, which delayed our '
                        'progress.'
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
            status=FeedbackStatusEnum.pending,  # Use the enum for status
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        ),
        SessionFeedback(
            id=uuid4(),
            session_id=sessions[1].id,  # Link to the second session
            scores={'structure': 76, 'empathy': 88, 'focus': 80, 'clarity': 81},
            tone_analysis={'positive': 80, 'neutral': 15, 'negative': 5},
            overall_score=90,
            transcript_uri='https://example.com/transcripts/session2.txt',
            speak_time_percent=55.0,
            questions_asked=7,
            session_length_s=2000,
            goals_achieved=4,
            example_positive=[
                {
                    'heading': 'Clear framing of the issue',
                    'feedback': (
                        'You effectively communicated the specific issue (missed deadlines) and its'
                        ' impact on the team without being accusatory.'
                    ),
                    'quote': (
                        'I’ve noticed that several deadlines were missed last week, and it’s '
                        'causing our team to fall behind on the overall project timeline.'
                    ),
                }
            ],
            example_negative=[
                {
                    'heading': 'Lack of specific examples',
                    'feedback': (
                        'While you mentioned missed deadlines, you didn’t provide specific '
                        'instances or data to illustrate the issue. Including concrete examples '
                        'would strengthen your feedback.'
                    ),
                    'quote': (
                        'The report due on Friday was submitted on Monday, which delayed our '
                        'progress.'
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
            status=FeedbackStatusEnum.pending,  # Use the enum for status
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        ),
    ]


def get_dummy_scenario_preparations(
    conversation_scenarios: list[ConversationScenario],
) -> list[ScenarioPreparation]:
    return [
        ScenarioPreparation(
            id=uuid4(),
            scenario_id=conversation_scenarios[0].id,
            objectives=[
                "Understand the client's needs",
                'Prepare a solution proposal',
            ],
            key_concepts=[
                {'header': 'Time management', 'value': 'Time management'},
                {'header': 'Collaboration', 'value': 'Collaboration'},
            ],
            prep_checklist=[
                'Review client history',
                'Prepare presentation slides',
            ],
            status=ScenarioPreparationStatus.pending,  # Use the enum for status
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        ),
        ScenarioPreparation(
            id=uuid4(),
            scenario_id=conversation_scenarios[1].id,
            objectives=[
                'Discuss project timeline',
                'Finalize deliverables',
            ],
            key_concepts=[
                {'header': 'Time management', 'value': 'Time management'},
                {'header': 'Collaboration', 'value': 'Collaboration'},
            ],
            prep_checklist=[
                'Prepare project timeline',
                'Review deliverables checklist',
            ],
            status=ScenarioPreparationStatus.pending,  # Use the enum for status
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        ),
    ]


def get_dummy_confidence_areas() -> list[ConfidenceArea]:
    """
    Generate dummy ConfidenceArea data.
    """
    return [
        ConfidenceArea(
            id=uuid4(),
            label='Giving difficult feedback',
            description='Confidence in providing constructive feedback in challenging situations.',
            min_value=0,
            max_value=100,
            min_label='Not confident',
            max_label='Very confident',
        ),
        ConfidenceArea(
            id=uuid4(),
            label='Managing team conflicts',
            description='Confidence in resolving conflicts within a team effectively.',
            min_value=0,
            max_value=100,
            min_label='Not confident',
            max_label='Very confident',
        ),
        ConfidenceArea(
            id=uuid4(),
            label='Leading challenging conversations',
            description='Confidence in leading conversations that require tact and diplomacy.',
            min_value=0,
            max_value=100,
            min_label='Not confident',
            max_label='Very confident',
        ),
    ]


def get_dummy_user_confidence_scores(
    user_profiles: list[UserProfile], confidence_areas: list[ConfidenceArea]
) -> list[UserConfidenceScore]:
    """
    Generate dummy UserConfidenceScore data.
    """
    scores = []
    for user in user_profiles:
        for area in confidence_areas:
            scores.append(
                UserConfidenceScore(
                    area_id=area.id,
                    user_id=user.id,
                    score=50,  # Default score for demonstration
                    updated_at=datetime.now(UTC),
                )
            )
    return scores


def get_dummy_app_configs() -> list[AppConfig]:
    """
    Generate dummy data for AppConfig.
    """
    return [
        AppConfig(key='dailyUserTokenLimit', value='100', type=ConfigType.int),
    ]
