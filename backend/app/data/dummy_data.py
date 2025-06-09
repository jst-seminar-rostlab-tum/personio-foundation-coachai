from datetime import UTC, datetime
from uuid import uuid4

from app.models.app_config import AppConfig, ConfigType
from app.models.confidence_area import ConfidenceArea
from app.models.conversation_category import ConversationCategory
from app.models.conversation_turn import ConversationTurn, SpeakerEnum
from app.models.difficulty_level import DifficultyLevel  # Assuming this is the new model
from app.models.experience import Experience
from app.models.goal import Goal
from app.models.language import Language  # Import the Language model
from app.models.learning_style import LearningStyle
from app.models.rating import Rating
from app.models.review import Review
from app.models.session_length import SessionLength
from app.models.training_case import TrainingCase, TrainingCaseStatus
from app.models.training_preparation import TrainingPreparation, TrainingPreparationStatus
from app.models.training_session import TrainingSession
from app.models.training_session_feedback import (
    FeedbackStatusEnum,
    TrainingSessionFeedback,
)
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


def get_dummy_session_lengths() -> list[SessionLength]:
    """
    Generate dummy SessionLength data.
    """
    return [
        SessionLength(
            id=uuid4(),
            label='30 minutes',
            description='Short session length for quick learning.',
        ),
        SessionLength(
            id=uuid4(),
            label='1 hour',
            description='Standard session length for detailed learning.',
        ),
        SessionLength(
            id=uuid4(),
            label='2 hours',
            description='Extended session length for in-depth learning.',
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
    session_lengths: list[SessionLength],
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
            preferred_session_length_id=session_lengths[0].id,
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
            preferred_session_length_id=session_lengths[1].id,
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


def get_dummy_reviews(
    user_profiles: list[UserProfile], training_sessions: list[TrainingSession]
) -> list[Review]:
    return [
        Review(
            id=uuid4(),
            user_id=user_profiles[0].id,
            session_id=training_sessions[0].id,  # Link to the first training session
            rating=5,
            comment='Excellent service!',
        ),
        Review(
            id=uuid4(),
            user_id=user_profiles[1].id,
            session_id=training_sessions[1].id,  # Link to a second training session
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


def get_dummy_training_cases(
    user_profiles: list[UserProfile], difficulty_levels: list[DifficultyLevel]
) -> list[TrainingCase]:
    return [
        TrainingCase(
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
            status=TrainingCaseStatus.draft,  # Use the enum instead of a string
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        ),
        TrainingCase(
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
            status=TrainingCaseStatus.draft,  # Use the enum instead of a string
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        ),
    ]


def get_dummy_ratings(
    training_sessions: list[TrainingSession], training_cases: list[TrainingCase]
) -> list[Rating]:
    # Create a mapping of case_id to user_id from the training_cases
    case_to_user_map = {case.id: case.user_id for case in training_cases}

    return [
        Rating(
            id=uuid4(),
            session_id=training_sessions[0].id,  # Link to the first training session
            user_id=case_to_user_map[
                training_sessions[0].case_id
            ],  # Get user_id from the training case
            score=5,
            comment='Excellent session!',
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        ),
        Rating(
            id=uuid4(),
            session_id=training_sessions[1].id,  # Link to the second training session
            user_id=case_to_user_map[
                training_sessions[1].case_id
            ],  # Get user_id from the training case
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
            name='Business',
            icon_uri='https://example.com/icons/business.png',
            system_prompt='You are a business consultant.',
            initial_prompt='What is your business challenge?',
            ai_setup={'type': 'business', 'complexity': 'high'},
            default_context='Business meeting with stakeholders.',
            default_goal='Improve communication and decision-making.',
            default_other_party='Stakeholders',
            is_custom=False,
            language_code='en',
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        ),
        ConversationCategory(
            id=uuid4(),
            name='Casual',
            icon_uri='https://example.com/icons/casual.png',
            system_prompt='You are a friendly conversationalist.',
            initial_prompt='How was your day?',
            ai_setup={'type': 'casual', 'complexity': 'low'},
            default_context='Casual conversation with a friend.',
            default_goal='Relax and enjoy the conversation.',
            default_other_party='Friend',
            is_custom=False,
            language_code='en',
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        ),
        ConversationCategory(
            id=uuid4(),
            name='Technical',
            icon_uri='https://example.com/icons/technical.png',
            system_prompt='You are a technical expert.',
            initial_prompt='What technical issue are you facing?',
            ai_setup={'type': 'technical', 'complexity': 'medium'},
            default_context='Technical discussion about software development.',
            default_goal='Solve technical problems efficiently.',
            default_other_party='Developer',
            is_custom=False,
            language_code='en',
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        ),
        ConversationCategory(
            id=uuid4(),
            name='Custom Category',
            icon_uri='https://example.com/icons/custom.png',
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


def get_dummy_conversation_turns(
    training_sessions: list[TrainingSession],
) -> list[ConversationTurn]:
    return [
        ConversationTurn(
            id=uuid4(),
            session_id=training_sessions[0].id,  # Link to the first training session
            speaker=SpeakerEnum.user,  # Use the SpeakerEnum for the speaker
            start_offset_ms=0,
            end_offset_ms=5000,
            text='Hello, how can I help you?',
            audio_uri='https://example.com/audio/user_hello.mp3',
            ai_emotion='neutral',
            created_at=datetime.now(UTC),
        ),
        ConversationTurn(
            id=uuid4(),
            session_id=training_sessions[1].id,  # Link to the second training session
            speaker=SpeakerEnum.ai,  # Use the SpeakerEnum for the speaker
            start_offset_ms=5000,
            end_offset_ms=10000,
            text='I need assistance with my account.',
            audio_uri='https://example.com/audio/system_assistance.mp3',
            ai_emotion='concerned',
            created_at=datetime.now(UTC),
        ),
    ]


def get_dummy_training_sessions(training_cases: list[TrainingCase]) -> list[TrainingSession]:
    return [
        TrainingSession(
            id=uuid4(),
            case_id=training_cases[0].id,
            scheduled_at=datetime.now(UTC),
            started_at=datetime.now(UTC),
            ended_at=datetime.now(UTC),
            language_code='en',  # Assuming "en" is a valid language code in the LanguageModel table
            ai_persona={'persona_name': 'AI Assistant', 'persona_role': 'Helper'},
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        ),
        TrainingSession(
            id=uuid4(),
            case_id=training_cases[1].id,
            scheduled_at=datetime.now(UTC),
            started_at=datetime.now(UTC),
            ended_at=datetime.now(UTC),
            language_code='de',  # Assuming "fr" is a valid language code in the LanguageModel table
            ai_persona={'persona_name': 'AI Mentor', 'persona_role': 'Guide'},
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        ),
    ]


def get_dummy_training_session_feedback(
    training_sessions: list[TrainingSession],
) -> list[TrainingSessionFeedback]:
    return [
        TrainingSessionFeedback(
            id=uuid4(),
            session_id=training_sessions[0].id,  # Link to the first training session
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
        TrainingSessionFeedback(
            id=uuid4(),
            session_id=training_sessions[1].id,  # Link to the second training session
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


def get_dummy_training_preparations(
    training_cases: list[TrainingCase],
) -> list[TrainingPreparation]:
    return [
        TrainingPreparation(
            id=uuid4(),
            case_id=training_cases[0].id,
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
            status=TrainingPreparationStatus.pending,  # Use the enum for status
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        ),
        TrainingPreparation(
            id=uuid4(),
            case_id=training_cases[1].id,
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
            status=TrainingPreparationStatus.pending,  # Use the enum for status
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
