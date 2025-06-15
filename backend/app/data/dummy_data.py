from datetime import UTC, datetime
from uuid import uuid4

from gotrue import AdminUserAttributes
from supabase import AuthError, create_client

from app.config import settings
from app.data.mock_user_ids_enum import MockUserIdsEnum
from app.models.admin_dashboard_stats import AdminDashboardStats
from app.models.app_config import AppConfig, ConfigType
from app.models.conversation_category import ConversationCategory
from app.models.conversation_scenario import (
    ConversationScenario,
    ConversationScenarioStatus,
    DifficultyLevel,
)
from app.models.language import LanguageCode
from app.models.rating import Rating
from app.models.review import Review
from app.models.scenario_preparation import ScenarioPreparation, ScenarioPreparationStatus
from app.models.session import Session, SessionStatus
from app.models.session_feedback import (
    FeedbackStatusEnum,
    SessionFeedback,
)
from app.models.session_turn import SessionTurn, SpeakerEnum
from app.models.user_confidence_score import ConfidenceArea, UserConfidenceScore
from app.models.user_goal import Goal, UserGoal
from app.models.user_profile import (
    AccountRole,
    Experience,
    PreferredLearningStyle,
    ProfessionalRole,
    UserProfile,
)


def get_dummy_user_profiles() -> list[UserProfile]:
    """
    Generate dummy UserProfile data.
    """
    return [
        UserProfile(
            id=MockUserIdsEnum.USER.value,
            preferred_language_code=LanguageCode.en,
            account_role=AccountRole.user,
            professional_role=ProfessionalRole.hr_professional,
            experience=Experience.beginner,
            preferred_learning_style=PreferredLearningStyle.visual,
            store_conversations=False,
            total_sessions=32,
            training_time=4.5,
            current_streak_days=3,
            average_score=82,
            goals_achieved=4,
        ),
        UserProfile(
            id=MockUserIdsEnum.ADMIN.value,
            preferred_language_code=LanguageCode.en,
            account_role=AccountRole.admin,
            professional_role=ProfessionalRole.executive,
            experience=Experience.expert,
            preferred_learning_style=PreferredLearningStyle.kinesthetic,
            store_conversations=True,
            total_sessions=5,
            training_time=4.2,
            current_streak_days=2,
            average_score=87,
            goals_achieved=2,
        ),
    ]


def get_dummy_user_goals(user_profiles: list[UserProfile]) -> list[UserGoal]:
    return [
        UserGoal(goal=Goal.giving_constructive_feedback, user_id=user_profiles[0].id),
        UserGoal(goal=Goal.managing_team_conflicts, user_id=user_profiles[0].id),
        UserGoal(goal=Goal.performance_reviews, user_id=user_profiles[0].id),
        UserGoal(goal=Goal.motivating_team_members, user_id=user_profiles[0].id),
        UserGoal(goal=Goal.leading_difficult_conversations, user_id=user_profiles[0].id),
        UserGoal(goal=Goal.communicating_organizational_change, user_id=user_profiles[0].id),
        UserGoal(goal=Goal.develop_emotional_intelligence, user_id=user_profiles[0].id),
        UserGoal(goal=Goal.giving_constructive_feedback, user_id=user_profiles[1].id),
        UserGoal(goal=Goal.managing_team_conflicts, user_id=user_profiles[1].id),
        UserGoal(goal=Goal.performance_reviews, user_id=user_profiles[1].id),
        UserGoal(goal=Goal.motivating_team_members, user_id=user_profiles[1].id),
        UserGoal(goal=Goal.leading_difficult_conversations, user_id=user_profiles[1].id),
        UserGoal(goal=Goal.communicating_organizational_change, user_id=user_profiles[1].id),
        UserGoal(goal=Goal.develop_emotional_intelligence, user_id=user_profiles[1].id),
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
            session_id=None,  # No session linked --> App Review
            rating=4,
            comment='Good overall, but could use more examples.',
        ),
        Review(
            id=uuid4(),
            user_id=user_profiles[0].id,
            session_id=None,  # No session linked --> App Review
            rating=4,
            comment='Great experience overall, but could use more examples.',
        ),
        Review(
            id=uuid4(),
            user_id=user_profiles[1].id,
            session_id=sessions[0].id,  # Link to the first session
            rating=3,
            comment='Good, but I expected more personalized feedback.',
        ),
        Review(
            id=uuid4(),
            user_id=user_profiles[0].id,
            session_id=sessions[1].id,  # Link to a second session
            rating=5,
            comment='Loved the interactive session and practical exercise!',
        ),
        Review(
            id=uuid4(),
            user_id=user_profiles[1].id,
            session_id=None,  # No session linked --> App Review
            rating=1,
            comment='Did not meet my expectations, too basic.',
        ),
        Review(
            id=uuid4(),
            user_id=user_profiles[0].id,
            session_id=None,  # No session linked --> App Review
            rating=4,
            comment='Very informative, but the pace was a bit slow.',
        ),
        Review(
            id=uuid4(),
            user_id=user_profiles[1].id,
            session_id=None,  # No session linked --> App Review
            rating=3,
            comment='Decent content, but I expected more depth.',
        ),
    ]


def get_dummy_conversation_scenarios(
    user_profiles: list[UserProfile], categories: list[ConversationCategory]
) -> list[ConversationScenario]:
    return [
        ConversationScenario(
            id=uuid4(),
            user_id=user_profiles[0].id,
            category_id=categories[0].id,
            custom_category_label='Custom Category 1',
            context='Context 1',
            goal='Goal 1',
            other_party='Other Party 1',
            difficulty_level=DifficultyLevel.easy,
            tone='Friendly',
            complexity='Low',
            status=ConversationScenarioStatus.draft,  # Use the enum instead of a string
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        ),
        ConversationScenario(
            id=uuid4(),
            user_id=user_profiles[1].id,
            category_id=categories[1].id,
            custom_category_label='Custom Category 2',
            context='Context 2',
            goal='Goal 2',
            other_party='Other Party 2',
            difficulty_level=DifficultyLevel.medium,
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
            id='giving_feedback',
            name='Giving Feedback',
            system_prompt='You are an expert in providing constructive feedback.',
            initial_prompt='What feedback challenge are you facing?',
            ai_setup={'type': 'feedback', 'complexity': 'medium'},
            default_context='One-on-one meeting with a team member.',
            default_goal='Provide constructive feedback effectively.',
            default_other_party='Team member',
            is_custom=False,
            language_code=LanguageCode.en,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        ),
        ConversationCategory(
            id='performance_reviews',
            name='Performance Reviews',
            system_prompt='You are a manager conducting performance reviews.',
            initial_prompt='What aspect of performance would you like to discuss?',
            ai_setup={'type': 'review', 'complexity': 'high'},
            default_context='Formal performance review meeting.',
            default_goal='Evaluate and discuss employee performance.',
            default_other_party='Employee',
            is_custom=False,
            language_code=LanguageCode.en,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        ),
        ConversationCategory(
            id='conflict_resolution',
            name='Conflict Resolution',
            system_prompt='You are a mediator resolving conflicts.',
            initial_prompt='What conflict are you trying to resolve?',
            ai_setup={'type': 'mediation', 'complexity': 'high'},
            default_context='Conflict resolution meeting between team members.',
            default_goal='Resolve conflicts and improve team dynamics.',
            default_other_party='Team members',
            is_custom=False,
            language_code=LanguageCode.en,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        ),
        ConversationCategory(
            id='salary_discussions',
            name='Salary Discussions',
            system_prompt='You are a negotiator discussing salary expectations.',
            initial_prompt='What salary-related topic would you like to address?',
            ai_setup={'type': 'negotiation', 'complexity': 'medium'},
            default_context='Salary negotiation meeting.',
            default_goal='Reach a mutually beneficial agreement on salary.',
            default_other_party='Employer',
            is_custom=False,
            language_code=LanguageCode.en,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        ),
        ConversationCategory(
            id='custom',
            name='Custom Category',
            system_prompt='',
            initial_prompt='',
            ai_setup={},
            default_context='',
            default_goal='',
            default_other_party='',
            is_custom=True,
            language_code=LanguageCode.en,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        ),
    ]


def get_dummy_session_turns(
    sessions: list[Session],
) -> list[SessionTurn]:
    return [
        # Session 1
        SessionTurn(
            id=uuid4(),
            session_id=sessions[0].id,
            speaker=SpeakerEnum.user,
            start_offset_ms=0,
            end_offset_ms=5000,
            text='Hello, how can I help you?',
            audio_uri='https://example.com/audio/user_hello.mp3',
            ai_emotion='neutral',
            created_at=datetime.now(UTC),
        ),
        SessionTurn(
            id=uuid4(),
            session_id=sessions[0].id,
            speaker=SpeakerEnum.ai,
            start_offset_ms=5000,
            end_offset_ms=10000,
            text='Hi! I’d like to check your schedule today. Are you available at 2 PM?',
            audio_uri='https://example.com/audio/ai_schedule_check.mp3',
            ai_emotion='friendly',
            created_at=datetime.now(UTC),
        ),
        SessionTurn(
            id=uuid4(),
            session_id=sessions[0].id,
            speaker=SpeakerEnum.user,
            start_offset_ms=10000,
            end_offset_ms=15000,
            text='Sure, 2 PM works fine.',
            audio_uri='https://example.com/audio/user_agree.mp3',
            ai_emotion='happy',
            created_at=datetime.now(UTC),
        ),
        # Session 2
        SessionTurn(
            id=uuid4(),
            session_id=sessions[1].id,
            speaker=SpeakerEnum.user,
            start_offset_ms=0,
            end_offset_ms=4000,
            text='I need assistance with my account.',
            audio_uri='https://example.com/audio/user_assistance.mp3',
            ai_emotion='concerned',
            created_at=datetime.now(UTC),
        ),
        SessionTurn(
            id=uuid4(),
            session_id=sessions[1].id,
            speaker=SpeakerEnum.ai,
            start_offset_ms=4000,
            end_offset_ms=9000,
            text='Of course. Could you please tell me what issue you are facing?',
            audio_uri='https://example.com/audio/ai_request_issue.mp3',
            ai_emotion='calm',
            created_at=datetime.now(UTC),
        ),
        SessionTurn(
            id=uuid4(),
            session_id=sessions[1].id,
            speaker=SpeakerEnum.user,
            start_offset_ms=9000,
            end_offset_ms=13000,
            text='I’m not able to log in since yesterday.',
            audio_uri='https://example.com/audio/user_login_issue.mp3',
            ai_emotion='worried',
            created_at=datetime.now(UTC),
        ),
        SessionTurn(
            id=uuid4(),
            session_id=sessions[1].id,
            speaker=SpeakerEnum.ai,
            start_offset_ms=13000,
            end_offset_ms=17000,
            text='Thanks for the info. I will reset your credentials and email you shortly.',
            audio_uri='https://example.com/audio/ai_reset_response.mp3',
            ai_emotion='helpful',
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
            ai_persona={'persona_name': 'AI Assistant', 'persona_role': 'Helper'},
            status=SessionStatus.started,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        ),
        Session(
            id=uuid4(),
            scenario_id=conversation_scenarios[1].id,
            scheduled_at=datetime.now(UTC),
            started_at=datetime.now(UTC),
            ended_at=datetime.now(UTC),
            ai_persona={'persona_name': 'AI Mentor', 'persona_role': 'Guide'},
            status=SessionStatus.started,
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
            status=FeedbackStatusEnum.completed,  # Use the enum for status
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
            status=FeedbackStatusEnum.completed,  # Use the enum for status
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
            status=ScenarioPreparationStatus.completed,  # Use the enum for status
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
            status=ScenarioPreparationStatus.completed,  # Use the enum for status
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        ),
    ]


def get_dummy_user_confidence_scores(user_profiles: list[UserProfile]) -> list[UserConfidenceScore]:
    """
    Generate dummy UserConfidenceScore data.
    """
    scores = []
    areas = list(ConfidenceArea)  # ['giving_difficult_feedback', 'managing_team_conflicts', ...]

    for user in user_profiles:
        for area in areas:
            scores.append(
                UserConfidenceScore(
                    confidence_area=area,
                    user_id=user.id,
                    score=50,
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


def get_dummy_admin_stats() -> list[AdminDashboardStats]:
    """
    Generate dummy admin stats data.
    """
    return [
        AdminDashboardStats(
            id=uuid4(),
            total_trainings=34533,
            average_score=86,
        )
    ]


def get_mock_user_data() -> tuple[AdminUserAttributes, AdminUserAttributes]:
    """
    Generate mock user data for testing purposes.
    """
    return (
        {
            'id': MockUserIdsEnum.USER.value.__str__(),
            'email': settings.MOCK_USER_DATA.email,
            'password': settings.MOCK_USER_DATA.password,
            'phone': settings.MOCK_USER_DATA.phone,
            'email_confirm': True,
            'phone_confirm': True,
            'user_metadata': {
                'full_name': settings.MOCK_USER_DATA.full_name,
            },
        },
        {
            'id': MockUserIdsEnum.ADMIN.value.__str__(),
            'email': settings.MOCK_ADMIN_DATA.email,
            'password': settings.MOCK_ADMIN_DATA.password,
            'phone': settings.MOCK_ADMIN_DATA.phone,
            'email_confirm': True,
            'phone_confirm': True,
            'user_metadata': {
                'full_name': settings.MOCK_ADMIN_DATA.full_name,
            },
        },
    )


def create_mock_users() -> None:
    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)

    attributes, admin_attributes = get_mock_user_data()

    # Create mock user
    try:
        supabase.auth.admin.create_user(attributes)
    except Exception as e:
        raise Exception(f'Error creating mock user {MockUserIdsEnum.USER.value}: {e}') from e

    # Create mock admin user
    try:
        supabase.auth.admin.create_user(admin_attributes)
    except Exception as e:
        raise Exception(f'Error creating mock admin user {MockUserIdsEnum.ADMIN.value}: {e}') from e


def delete_mock_users() -> None:
    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
    for user_id in [MockUserIdsEnum.USER.value, MockUserIdsEnum.ADMIN.value]:
        try:
            supabase.auth.admin.delete_user(user_id.__str__())
        except AuthError as e:
            if e.code != 'user_not_found':
                raise e
        except Exception as e:
            raise e
