from datetime import datetime
from uuid import uuid4

from backend.models.conversation_category import ConversationCategory
from backend.models.conversation_turn import ConversationTurn, SpeakerEnum
from backend.models.difficulty_level import DifficultyLevel  # Assuming this is the new model
from backend.models.experience import Experience
from backend.models.goal import Goal
from backend.models.language import Language  # Import the Language model
from backend.models.rating import Rating
from backend.models.role import Role
from backend.models.training_case import TrainingCase, TrainingCaseStatus
from backend.models.training_preparation import TrainingPreparation, TrainingPreparationStatus
from backend.models.training_session import TrainingSession
from backend.models.training_session_feedback import (
    FeedbackStatusEnum,
    TrainingSessionFeedback,
)
from backend.models.user_goal import UserGoal
from backend.models.user_profile import UserProfile


def get_dummy_languages() -> list[Language]:
    return [
        Language(code='en', name='English'),
        Language(code='de', name='German'),
    ]


def get_dummy_roles() -> list[Role]:
    return [
        Role(id=uuid4(), label='Admin', description='Administrator role'),
        Role(id=uuid4(), label='User', description='Regular user role'),
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


def get_dummy_user_profiles(roles: list[Role], experiences: list[Experience]) -> list[UserProfile]:
    return [
        UserProfile(
            id=uuid4(),
            preferred_language='en',
            role_id=roles[0].id,
            experience_id=experiences[0].id,
            preferred_learning_style='Visual',
            preferred_session_length='30 minutes',
            total_sessions=32,
            training_time=4.5,
            current_streak_days=3,
            average_score=82,
            goals_achieved=4,
        ),
        UserProfile(
            id=uuid4(),
            preferred_language='de',
            role_id=roles[1].id,
            experience_id=experiences[1].id,
            preferred_learning_style='Auditory',
            preferred_session_length='1 hour',
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


def get_dummy_training_cases(
    user_profiles: list[UserProfile], difficulty_levels: list[DifficultyLevel]
) -> list[TrainingCase]:
    return [
        TrainingCase(
            id=uuid4(),
            user_id=user_profiles[0].id,
            category_id=None,
            scenario_template_id=None,
            custom_category_label='Custom Category 1',
            context='Context 1',
            goal='Goal 1',
            other_party='Other Party 1',
            difficulty_id=difficulty_levels[0].id,
            tone='Friendly',
            complexity='Low',
            status=TrainingCaseStatus.draft,  # Use the enum instead of a string
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        ),
        TrainingCase(
            id=uuid4(),
            user_id=user_profiles[1].id,
            category_id=None,
            scenario_template_id=None,
            custom_category_label='Custom Category 2',
            context='Context 2',
            goal='Goal 2',
            other_party='Other Party 2',
            difficulty_id=difficulty_levels[1].id,
            tone='Professional',
            complexity='Medium',
            status=TrainingCaseStatus.draft,  # Use the enum instead of a string
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
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
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        ),
        Rating(
            id=uuid4(),
            session_id=training_sessions[1].id,  # Link to the second training session
            user_id=case_to_user_map[
                training_sessions[1].case_id
            ],  # Get user_id from the training case
            score=4,
            comment='Good session, but room for improvement.',
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        ),
    ]


def get_dummy_conversation_categories() -> list[ConversationCategory]:
    return [
        ConversationCategory(
            id=uuid4(),
            name='Business',
            icon_uri='https://example.com/icons/business.png',
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        ),
        ConversationCategory(
            id=uuid4(),
            name='Casual',
            icon_uri='https://example.com/icons/casual.png',
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        ),
        ConversationCategory(
            id=uuid4(),
            name='Technical',
            icon_uri='https://example.com/icons/technical.png',
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
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
            created_at=datetime.utcnow(),
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
            created_at=datetime.utcnow(),
        ),
    ]


def get_dummy_training_sessions(training_cases: list[TrainingCase]) -> list[TrainingSession]:
    return [
        TrainingSession(
            id=uuid4(),
            case_id=training_cases[0].id,
            scheduled_at=datetime.utcnow(),
            started_at=datetime.utcnow(),
            ended_at=datetime.utcnow(),
            language_code='en',  # Assuming "en" is a valid language code in the LanguageModel table
            ai_persona={'persona_name': 'AI Assistant', 'persona_role': 'Helper'},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        ),
        TrainingSession(
            id=uuid4(),
            case_id=training_cases[1].id,
            scheduled_at=datetime.utcnow(),
            started_at=datetime.utcnow(),
            ended_at=datetime.utcnow(),
            language_code='de',  # Assuming "fr" is a valid language code in the LanguageModel table
            ai_persona={'persona_name': 'AI Mentor', 'persona_role': 'Guide'},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        ),
    ]


def get_dummy_training_session_feedback(
    training_sessions: list[TrainingSession],
) -> list[TrainingSessionFeedback]:
    return [
        TrainingSessionFeedback(
            id=uuid4(),
            session_id=training_sessions[0].id,  # Link to the first training session
            scores={'clarity': 8, 'engagement': 7, 'accuracy': 9},
            tone_analysis={'positive': 70, 'neutral': 20, 'negative': 10},
            overall_score=85,
            transcript_uri='https://example.com/transcripts/session1.txt',
            speak_time_percent=60.5,
            questions_asked=5,
            session_length_s=1800,
            goals_achieved=3,
            examples_positive='### Clear framing of the issue You effectively communicated the '
            'specific issue (missed deadlines) and its impact on the team without being '
            'accusatory. > “I’ve noticed that several deadlines were missed last week, and '
            'it’s causing our team to fall behind on the overall project timeline.” --- ',
            examples_negative='### Lack of specific examples While you mentioned missed '
            'deadlines, you didn’t provide specific instances or data to illustrate the issue. '
            'Including concrete examples would strengthen your feedback. > “For example, the '
            'report due on Friday was submitted on Monday, which delayed our progress.” --- ',
            recommendations='### Practice the STAR method When giving feedback, use the c '
            'Situation, Task, Action, Result framework to provide more concrete examples. '
            '--- ### Ask more diagnostic questions Spend more time understanding root causes '
            'before moving to solutions. This builds empathy and leads to more effective '
            'outcomes.  --- ### Define next steps End feedback conversations with agreed-upon',
            status=FeedbackStatusEnum.pending,  # Use the enum for status
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        ),
        TrainingSessionFeedback(
            id=uuid4(),
            session_id=training_sessions[1].id,  # Link to the second training session
            scores={'clarity': 9, 'engagement': 8, 'accuracy': 8},
            tone_analysis={'positive': 80, 'neutral': 15, 'negative': 5},
            overall_score=90,
            transcript_uri='https://example.com/transcripts/session2.txt',
            speak_time_percent=55.0,
            questions_asked=7,
            session_length_s=2000,
            goals_achieved=4,
            examples_positive='### Clear framing of the issue You effectively communicated the '
            'specific issue (missed deadlines) and its impact on the team without being '
            'accusatory. > “I’ve noticed that several deadlines were missed last week, and '
            'it’s causing our team to fall behind on the overall project timeline.” --- ',
            examples_negative='### Lack of specific examples While you mentioned missed '
            'deadlines, you didn’t provide specific instances or data to illustrate the issue. '
            'Including concrete examples would strengthen your feedback. > “For example, the '
            'report due on Friday was submitted on Monday, which delayed our progress.” --- ',
            recommendations='### Practice the STAR method When giving feedback, use the c '
            'Situation, Task, Action, Result framework to provide more concrete examples. '
            '--- ### Ask more diagnostic questions Spend more time understanding root causes '
            'before moving to solutions. This builds empathy and leads to more effective '
            'outcomes.  --- ### Define next steps End feedback conversations with agreed-upon',
            status=FeedbackStatusEnum.pending,  # Use the enum for status
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        ),
    ]


def get_dummy_training_preparations(
    training_cases: list[TrainingCase],
) -> list[TrainingPreparation]:
    return [
        TrainingPreparation(
            id=uuid4(),
            case_id=training_cases[0].id,
            objectives={
                'objective_1': "Understand the client's needs",
                'objective_2': 'Prepare a solution proposal',
            },
            key_concepts='### SBI Framework - **Situation**: Describe the specific situation.',
            prep_checklist={
                'item_1': 'Review client history',
                'item_2': 'Prepare presentation slides',
            },
            status=TrainingPreparationStatus.pending,  # Use the enum for status
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        ),
        TrainingPreparation(
            id=uuid4(),
            case_id=training_cases[1].id,
            objectives={
                'objective_1': 'Discuss project timeline',
                'objective_2': 'Finalize deliverables',
            },
            key_concepts='### SBI Framework - **Situation**: Describe the specific situation.',
            prep_checklist={
                'item_1': 'Prepare project timeline',
                'item_2': 'Review deliverables checklist',
            },
            status=TrainingPreparationStatus.pending,  # Use the enum for status
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        ),
    ]
