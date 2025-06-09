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
from app.models.role import Role
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
      Generate dummy LearningStyle data with multi-language support.
      """
    visual_id = uuid4()
    auditory_id = uuid4()
    kinesthetic_id = uuid4()

    return [
        # Visual
        LearningStyle(
            id=visual_id,
            language_code="en",
            label="Visual",
            description="Prefers learning through visual aids like diagrams and charts."
        ),
        LearningStyle(
            id=visual_id,
            language_code="de",
            label="Visuell",
            description="Lernt bevorzugt mit visuellen Hilfsmitteln wie Diagrammen und Grafiken."
        ),

        # Auditory
        LearningStyle(
            id=auditory_id,
            language_code="en",
            label="Auditory",
            description="Prefers learning through listening to explanations and discussions."
        ),
        LearningStyle(
            id=auditory_id,
            language_code="de",
            label="Auditiv",
            description="Lernt bevorzugt durch Zuhören von Erklärungen und Diskussionen."
        ),

        # Kinesthetic
        LearningStyle(
            id=kinesthetic_id,
            language_code="en",
            label="Kinesthetic",
            description="Prefers learning through hands-on activities and physical engagement."
        ),
        LearningStyle(
            id=kinesthetic_id,
            language_code="de",
            label="Kinästhetisch",
            description="Lernt bevorzugt durch praktische Aktivitäten und körperliches Engagement."
        ),
    ]


def get_dummy_session_lengths() -> list[SessionLength]:
    """
    Generate dummy SessionLength data.
    """
    id1 = uuid4()
    id2 = uuid4()
    id3 = uuid4()

    return [
        SessionLength(
            id=id1,
            language_code='en',
            label='30 minutes',
            description='Short session length for quick learning.',
        ),
        SessionLength(
            id=id1,
            language_code='de',
            label='30 Minuten',
            description='Kurze Sitzungsdauer für schnelles Lernen.',
        ),
        SessionLength(
            id=id2,
            language_code='en',
            label='1 hour',
            description='Standard session length for detailed learning.',
        ),
        SessionLength(
            id=id2,
            language_code='de',
            label='1 Stunde',
            description='Standard-Sitzungsdauer für detailliertes Lernen.',
        ),
        SessionLength(
            id=id3,
            language_code='en',
            label='2 hours',
            description='Extended session length for in-depth learning.',
        ),
        SessionLength(
            id=id3,
            language_code='de',
            label='2 Stunden',
            description='Erweiterte Sitzungsdauer für vertieftes Lernen.',
        ),
    ]


def get_dummy_languages() -> list[Language]:
    return [
        Language(code='en', name='English'),
        Language(code='de', name='German'),
    ]


def get_dummy_experiences() -> list[Experience]:
    beginner_id = uuid4()
    intermediate_id = uuid4()
    expert_id = uuid4()

    return [
        # Beginner
        Experience(id=beginner_id, language_code="en", label="Beginner",
                   description="New to the field"),
        Experience(id=beginner_id, language_code="de", label="Anfänger",
                   description="Neu auf dem Gebiet"),

        # Intermediate
        Experience(id=intermediate_id, language_code="en", label="Intermediate",
                   description="Some experience"),
        Experience(id=intermediate_id, language_code="de", label="Fortgeschritten",
                   description="Etwas Erfahrung"),

        # Expert
        Experience(id=expert_id, language_code="en", label="Expert",
                   description="Highly experienced"),
        Experience(id=expert_id, language_code="de", label="Experte", description="Sehr erfahren"),
    ]


def get_dummy_roles() -> list[Role]:
    """
    Generate multilingual dummy Role data for both English and German.
    Each role has the same UUID across languages.
    """
    hr_id = uuid4()
    leader_id = uuid4()
    exec_id = uuid4()
    other_id = uuid4()

    return [
        # HR Professional
        Role(id=hr_id, language_code="en", label="HR Professional",
             description="I work in human resources or people operations."),
        Role(id=hr_id, language_code="de", label="HR-Fachkraft",
             description="Ich arbeite im Bereich Personalwesen oder Personalmanagement."),

        # Team Leader
        Role(id=leader_id, language_code="en", label="Team Leader",
             description="I manage a team or department."),
        Role(id=leader_id, language_code="de", label="Teamleiter:in",
             description="Ich leite ein Team oder eine Abteilung."),

        # Executive
        Role(id=exec_id, language_code="en", label="Executive",
             description="I’m a director, VP, or C-level executive."),
        Role(id=exec_id, language_code="de", label="Führungskraft",
             description="Ich bin Direktor:in, VP oder Teil der Geschäftsleitung."),

        # Other
        Role(id=other_id, language_code="en", label="Other",
             description="None of them above"),
        Role(id=other_id, language_code="de", label="Andere",
             description="Keine der oben genannten Optionen."),
    ]


def get_dummy_goals() -> list[Goal]:
    goal1_id = uuid4()
    goal2_id = uuid4()
    return [
        # Goal 1: Improve Communication
        Goal(
            id=goal1_id,
            language_code='en',
            label='Improve Communication',
            description='Focus on verbal and non-verbal communication skills.',
        ),
        Goal(
            id=goal1_id,
            language_code='de',
            label='Kommunikation verbessern',
            description='Konzentriere dich auf verbale und nonverbale Kommunikation.',
        ),

        # Goal 2: Time Management
        Goal(
            id=goal2_id,
            language_code='en',
            label='Time Management',
            description='Improve productivity and manage time effectively.',
        ),
        Goal(
            id=goal2_id,
            language_code='de',
            label='Zeitmanagement',
            description='Produktivität verbessern und Zeit effektiv nutzen.',
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
        roles: list[Role]
) -> list[UserProfile]:
    """
    Generate dummy UserProfile data.
    """
    return [
        UserProfile(
            id=uuid4(),
            preferred_language='en',
            user_role=UserRole.user,
            experience_id=experiences[0].id,
            preferred_learning_style_id=learning_styles[0].id,
            preferred_session_length_id=session_lengths[0].id,
            role_id=roles[0].id,
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
            user_role=UserRole.admin,
            experience_id=experiences[1].id,
            preferred_learning_style_id=learning_styles[1].id,
            preferred_session_length_id=session_lengths[1].id,
            role_id=roles[1].id,
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
                        'You effectively communicated the specific issue (missed deadlines) '
                        'and its impact on the team without being accusatory.'
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
    common_id_1 = uuid4()
    common_id_2 = uuid4()
    common_id_3 = uuid4()

    return [
        # English Versions
        ConfidenceArea(
            id=common_id_1,
            language_code='en',
            label='Giving difficult feedback',
            description='Confidence in providing constructive feedback in challenging situations.',
            min_value=0,
            max_value=100,
            min_label='Not confident',
            max_label='Very confident',
        ),
        ConfidenceArea(
            id=common_id_2,
            language_code='en',
            label='Managing team conflicts',
            description='Confidence in resolving conflicts within a team effectively.',
            min_value=0,
            max_value=100,
            min_label='Not confident',
            max_label='Very confident',
        ),
        ConfidenceArea(
            id=common_id_3,
            language_code='en',
            label='Leading challenging conversations',
            description='Confidence in leading conversations that require tact and diplomacy.',
            min_value=0,
            max_value=100,
            min_label='Not confident',
            max_label='Very confident',
        ),

        # German Versions
        ConfidenceArea(
            id=common_id_1,
            language_code='de',
            label='Schwieriges Feedback geben',
            description='Selbstvertrauen beim Geben von konstruktivem Feedback in '
                        'herausfordernden Situationen.',
            min_value=0,
            max_value=100,
            min_label='Nicht selbstbewusst',
            max_label='Sehr selbstbewusst',
        ),
        ConfidenceArea(
            id=common_id_2,
            language_code='de',
            label='Konflikte im Team managen',
            description='Selbstvertrauen im effektiven Lösen von Konflikten innerhalb eines Teams.',
            min_value=0,
            max_value=100,
            min_label='Nicht selbstbewusst',
            max_label='Sehr selbstbewusst',
        ),
        ConfidenceArea(
            id=common_id_3,
            language_code='de',
            label='Herausfordernde Gespräche führen',
            description='Selbstvertrauen beim Führen von Gesprächen, die Taktgefühl '
                        'und Diplomatie erfordern.',
            min_value=0,
            max_value=100,
            min_label='Nicht selbstbewusst',
            max_label='Sehr selbstbewusst',
        ),
    ]


def get_dummy_user_confidence_scores(
        user_profiles: list[UserProfile], confidence_areas: list[ConfidenceArea]
) -> list[UserConfidenceScore]:
    """
    Generate dummy UserConfidenceScore data.
    """
    # To filter out different languages for the same case
    unique_areas_by_id = {}
    for area in confidence_areas:
        if area.id not in unique_areas_by_id:
            unique_areas_by_id[area.id] = area

    scores = []
    for user in user_profiles:
        for area in unique_areas_by_id.values():
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
