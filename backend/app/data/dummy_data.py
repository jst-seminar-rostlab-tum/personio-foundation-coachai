import json
import os
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from gotrue import AdminUserAttributes
from supabase import AuthError

from app.config import settings
from app.database import get_supabase_client
from app.enums.account_role import AccountRole
from app.enums.confidence_area import ConfidenceArea
from app.enums.config_type import ConfigType
from app.enums.conversation_scenario_status import ConversationScenarioStatus
from app.enums.difficulty_level import DifficultyLevel
from app.enums.experience import Experience
from app.enums.feedback_status import FeedbackStatus
from app.enums.goal import Goal
from app.enums.language import LanguageCode
from app.enums.preferred_learning_style import PreferredLearningStyle
from app.enums.professional_role import ProfessionalRole
from app.enums.scenario_preparation_status import ScenarioPreparationStatus
from app.enums.session_status import SessionStatus
from app.enums.speaker import SpeakerType
from app.interfaces import MockUserIdsEnum
from app.models import LiveFeedback
from app.models.admin_dashboard_stats import AdminDashboardStats
from app.models.app_config import AppConfig
from app.models.conversation_category import ConversationCategory
from app.models.conversation_scenario import ConversationScenario
from app.models.review import Review
from app.models.scenario_preparation import ScenarioPreparation
from app.models.session import Session
from app.models.session_feedback import SessionFeedback
from app.models.session_turn import SessionTurn
from app.models.user_confidence_score import UserConfidenceScore
from app.models.user_goal import UserGoal
from app.models.user_profile import UserProfile


def get_dummy_user_profiles() -> list[UserProfile]:
    """
    Generate dummy UserProfile data.
    """
    return [
        UserProfile(
            id=MockUserIdsEnum.USER.value,
            full_name=settings.mock_user_data.full_name,
            email=settings.mock_user_data.email,
            phone_number=settings.mock_user_data.phone,
            preferred_language_code=LanguageCode.en,
            account_role=AccountRole.user,
            professional_role=ProfessionalRole.hr_professional,
            experience=Experience.beginner,
            preferred_learning_style=PreferredLearningStyle.visual,
            last_logged_in=datetime.now(UTC) - timedelta(days=2),
            store_conversations=False,
            total_sessions=32,
            training_time=4.5,
            current_streak_days=5,
            score_sum=32 * 82,
            goals_achieved=4,  # Summation of all goals achieved
        ),
        UserProfile(
            id=MockUserIdsEnum.ADMIN.value,
            full_name=settings.mock_admin_data.full_name,
            email=settings.mock_admin_data.email,
            phone_number=settings.mock_admin_data.phone,
            preferred_language_code=LanguageCode.en,
            account_role=AccountRole.admin,
            professional_role=ProfessionalRole.executive,
            experience=Experience.expert,
            preferred_learning_style=PreferredLearningStyle.kinesthetic,
            last_logged_in=datetime.now(UTC) - timedelta(days=2),
            store_conversations=True,
            total_sessions=5,
            training_time=4.2,
            current_streak_days=2,
            score_sum=5 * 87,
            goals_achieved=2,  # Summation of all goals achieved
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
            category_id=categories[0].id,  # Giving Feedback
            persona="""
                **Name**: Angry Alex
                **Personality**: Confrontational, defensive, emotionally volatile
                **Behavioral Traits**:
                - Assumes bad intent
                - Easily offended, especially with criticism
                - Challenges authority or decisions
                - Might raise voice
                **Training Focus**:
                - De-escalation techniques
                - Delivering negative feedback calmly
                - Maintaining control in heated situations
                - Validating emotions without losing authority
                **Company Position**: Development Coordinator (5 years experience)""",
            situational_facts="""
                **Missed Deadlines**
                - Quarterly partner-impact report arrived 5 days late despite reminders.
                - Field-visit summary incomplete; colleague had to rewrite it under pressure.

                **Attendance**
                - In the last 2 months, Alex skipped 4 of 8 team check-ins without notice.
                - When present, often keeps camera off and engages minimally.
                
                **Peer Feedback**
                - Two colleagues needed multiple nudges for inputs.
                - One now avoids assigning shared tasks to Alex due to reliability concerns.
                
                **Prior Support**
                - Six weeks ago, the manager set clear expectations and a prioritization plan.
                - Calendar tips and admin help were offered; little improvement seen.

                **Silver Lining**
                - Alex shows real creativity in outreach planning and still has growth potential.
            """,
            difficulty_level=DifficultyLevel.easy,
            status=ConversationScenarioStatus.draft,  # Use the enum instead of a string
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        ),
        ConversationScenario(
            id=uuid4(),
            user_id=user_profiles[1].id,
            category_id=categories[1].id,  # Performance Review
            custom_category_label='Custom Category 2',
            persona="""
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
                
                **Company Position**: Development Coordinator (5 years experience)""",
            situational_facts="""
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

            """,
            difficulty_level=DifficultyLevel.medium,
            status=ConversationScenarioStatus.draft,  # Use the enum instead of a string
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        ),
        ConversationScenario(
            id=uuid4(),
            user_id=user_profiles[0].id,
            category_id=categories[2].id,  # Conflict Resolution
            persona="""
                **Name**: Casual Candice
                **Personality**: Laid-back, informal, friendly but sometimes unfocused
                **Behavioral Traits**:
                - Uses humor or casual language
                - May not take feedback seriously
                - Tends to deflect or joke under pressure
                - Values flexibility over structure
                **Training Focus**:
                - Redirecting conversations professionally
                - Setting boundaries and expectations
                - Addressing underperformance without being overly formal
                - Keeping focus during relaxed interactions
                **Company Position**: Development Coordinator (5 years experience)""",
            situational_facts="""
                **Conflict Background**
                - Candice and Jordan collaborated on a partner event that went off-track due to 
                miscommunication.
                - Candice feels Jordan oversteps boundaries and takes credit for ideas.
                - Jordan has privately complained that Candice misses deadlines and ignores 
                messages.

                **Prior Attempts**
                - Two team meetings were held to clarify roles; tension persists.
                - Candice agreed to share updates more frequently; Jordan promised to check before 
                redoing Candice's work.

                **Current Impact**
                - Other teammates feel awkward and avoid putting Candice and Jordan on the same 
                tasks.
                - The manager is under pressure to ensure team cohesion before a major donor site 
                visit.

                **Silver Lining**
                - Both Candice and Jordan care deeply about partner success and have complementary 
                skills when working well together.

            """,
            difficulty_level=DifficultyLevel.easy,
            status=ConversationScenarioStatus.draft,  # Use the enum instead of a string
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        ),
        ConversationScenario(
            id=uuid4(),
            user_id=user_profiles[0].id,
            category_id=categories[3].id,  # Salary Discussion
            persona="""
                **Name**: Shy Sandra
                **Personality**: Quiet, reserved, conflict-avoidant, anxious about saying the wrong
                  thing
                **Behavioral Traits:**
                - Speaks in a soft, hesitant voice with frequent pauses
                - Uses filler words ("um…", "I guess…", "maybe…") and trails off mid-sentenceAgrees 
                verbally ("yeah… sure… okay") even when uncertain or uncomfortable
                - Avoids asserting opinions or asking questions
                - Long silences when asked direct or emotional questions
                - May apologize unnecessarily or downplay her own contributions
                **Training Focus:**
                - Encouraging open and honest communication through tone and phrasing
                - Actively checking for true understanding and comfort (not just verbal agreement)
                - Using silence constructively without rushing to fill it
                - Creating psychological safety so Sandra feels safe to speak up
                - Practicing empathetic, patient listening
                - Learning to gently draw out insights from passive participants
                **Company Position**: Development Coordinator (5 years experience)""",
            situational_facts="""
                **Current Salary**
                - Sandra earns slightly below the midpoint for Program Officers in this NGO.
                - Last annual raise was 4%.

                **Performance Context**
                - Solid on creative outreach and community partnerships.
                - Mixed record on deadlines and internal coordination.

                **Recent Request**
                - Last week, Sandra emailed HR asking for a 10% raise, citing cost of living and 
                workload growth.

                **Organizational Context**
                - The NGO faces tight budgets due to a new funder's spending cap.
                - Managers can approve up to 3% merit raise without director sign-off.

                **Silver Lining**
                - Peers respect Sandra's community engagement; manager has praised initiative on 
                outreach campaigns.
            """,
            difficulty_level=DifficultyLevel.easy,
            status=ConversationScenarioStatus.draft,  # Use the enum instead of a string
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        ),
    ]


def get_dummy_conversation_categories() -> list[ConversationCategory]:
    # Load context from JSON file
    initial_prompt_path = os.path.join(os.path.dirname(__file__), 'initial_prompts.json')
    try:
        with open(initial_prompt_path, encoding='utf-8') as f:
            initial_prompt_data = json.load(f)
    except Exception:
        initial_prompt_data = {}

    return [
        ConversationCategory(
            id='giving_feedback',
            name='Giving Feedback',
            initial_prompt=initial_prompt_data.get(
                'giving_feedback', 'One-on-one meeting with a team member.'
            ),
            is_custom=False,
            language_code=LanguageCode.en,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        ),
        ConversationCategory(
            id='performance_reviews',
            name='Performance Reviews',
            initial_prompt=initial_prompt_data.get(
                'performance_reviews', 'Formal performance review meeting.'
            ),
            is_custom=False,
            language_code=LanguageCode.en,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        ),
        ConversationCategory(
            id='conflict_resolution',
            name='Conflict Resolution',
            initial_prompt=initial_prompt_data.get(
                'conflict_resolution', 'Conflict resolution meeting between team members.'
            ),
            is_custom=False,
            language_code=LanguageCode.en,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        ),
        ConversationCategory(
            id='salary_discussions',
            name='Salary Discussions',
            initial_prompt=initial_prompt_data.get(
                'salary_discussions', 'Salary negotiation meeting.'
            ),
            is_custom=False,
            language_code=LanguageCode.en,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        ),
        ConversationCategory(
            id='custom',
            name='Custom Category',
            initial_prompt='',
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
            speaker=SpeakerType.user,
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
            speaker=SpeakerType.assistant,
            start_offset_ms=5000,
            end_offset_ms=10000,
            text="Hi! I'd like to check your schedule today. Are you available at 2 PM?",
            audio_uri='https://example.com/audio/ai_schedule_check.mp3',
            ai_emotion='friendly',
            created_at=datetime.now(UTC),
        ),
        SessionTurn(
            id=uuid4(),
            session_id=sessions[0].id,
            speaker=SpeakerType.user,
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
            speaker=SpeakerType.user,
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
            speaker=SpeakerType.assistant,
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
            speaker=SpeakerType.user,
            start_offset_ms=9000,
            end_offset_ms=13000,
            text="I'm not able to log in since yesterday.",
            audio_uri='https://example.com/audio/user_login_issue.mp3',
            ai_emotion='worried',
            created_at=datetime.now(UTC),
        ),
        SessionTurn(
            id=uuid4(),
            session_id=sessions[1].id,
            speaker=SpeakerType.assistant,
            start_offset_ms=13000,
            end_offset_ms=17000,
            text='Thanks for the info. I will reset your credentials and email you shortly.',
            audio_uri='https://example.com/audio/ai_reset_response.mp3',
            ai_emotion='helpful',
            created_at=datetime.now(UTC),
        ),
        # Session 3
        SessionTurn(
            id=uuid4(),
            session_id=sessions[2].id,
            speaker=SpeakerType.user,
            start_offset_ms=0,
            end_offset_ms=3000,
            text='Can you prepare the sales report by end of day?',
            audio_uri='https://example.com/audio/manager_request_report.mp3',
            ai_emotion='attentive',
            created_at=datetime.now(UTC),
        ),
        SessionTurn(
            id=uuid4(),
            session_id=sessions[2].id,
            speaker=SpeakerType.assistant,
            start_offset_ms=3000,
            end_offset_ms=7000,
            text="Absolutely. I'll make sure to include the latest figures.",
            audio_uri='https://example.com/audio/employee_confirm_report.mp3',
            ai_emotion='motivated',
            created_at=datetime.now(UTC),
        ),
        SessionTurn(
            id=uuid4(),
            session_id=sessions[2].id,
            speaker=SpeakerType.user,
            start_offset_ms=7000,
            end_offset_ms=10000,
            text='Good. Please double-check the Q2 numbers.',
            audio_uri='https://example.com/audio/manager_followup_q2.mp3',
            ai_emotion='firm',
            created_at=datetime.now(UTC),
        ),
        SessionTurn(
            id=uuid4(),
            session_id=sessions[2].id,
            speaker=SpeakerType.assistant,
            start_offset_ms=10000,
            end_offset_ms=13500,
            text="Will do. I'll send you a draft in a couple of hours.",
            audio_uri='https://example.com/audio/employee_confirm_draft.mp3',
            ai_emotion='reliable',
            created_at=datetime.now(UTC),
        ),
        # Session 4
        SessionTurn(
            id=uuid4(),
            session_id=sessions[3].id,
            speaker=SpeakerType.user,
            start_offset_ms=0,
            end_offset_ms=2800,
            text="How's the client presentation coming along?",
            audio_uri='https://example.com/audio/manager_check_presentation.mp3',
            ai_emotion='inquisitive',
            created_at=datetime.now(UTC),
        ),
        SessionTurn(
            id=uuid4(),
            session_id=sessions[3].id,
            speaker=SpeakerType.assistant,
            start_offset_ms=2800,
            end_offset_ms=6500,
            text="I've finished most of the slides. Just adding the final data now.",
            audio_uri='https://example.com/audio/employee_update_presentation.mp3',
            ai_emotion='focused',
            created_at=datetime.now(UTC),
        ),
        SessionTurn(
            id=uuid4(),
            session_id=sessions[3].id,
            speaker=SpeakerType.user,
            start_offset_ms=6500,
            end_offset_ms=9500,
            text='Great. Make sure the figures are up-to-date.',
            audio_uri='https://example.com/audio/manager_instruction_figures.mp3',
            ai_emotion='directive',
            created_at=datetime.now(UTC),
        ),
        SessionTurn(
            id=uuid4(),
            session_id=sessions[3].id,
            speaker=SpeakerType.assistant,
            start_offset_ms=9500,
            end_offset_ms=12800,
            text="Understood. I'll send it for your review by 3 PM.",
            audio_uri='https://example.com/audio/employee_confirm_review.mp3',
            ai_emotion='proactive',
            created_at=datetime.now(UTC),
        ),
        # Session 5
        SessionTurn(
            id=uuid4(),
            session_id=sessions[4].id,
            speaker=SpeakerType.user,
            start_offset_ms=0,
            end_offset_ms=3200,
            text='Did you submit your leave request for next week?',
            audio_uri='https://example.com/audio/manager_ask_leave.mp3',
            ai_emotion='neutral',
            created_at=datetime.now(UTC),
        ),
        SessionTurn(
            id=uuid4(),
            session_id=sessions[4].id,
            speaker=SpeakerType.assistant,
            start_offset_ms=3200,
            end_offset_ms=6000,
            text='Yes, I submitted it yesterday. Waiting for approval.',
            audio_uri='https://example.com/audio/employee_confirm_leave.mp3',
            ai_emotion='hopeful',
            created_at=datetime.now(UTC),
        ),
        SessionTurn(
            id=uuid4(),
            session_id=sessions[4].id,
            speaker=SpeakerType.user,
            start_offset_ms=6000,
            end_offset_ms=9000,
            text='Alright. Make sure all your tasks are handed over before you go.',
            audio_uri='https://example.com/audio/manager_reminder_tasks.mp3',
            ai_emotion='responsible',
            created_at=datetime.now(UTC),
        ),
        SessionTurn(
            id=uuid4(),
            session_id=sessions[4].id,
            speaker=SpeakerType.assistant,
            start_offset_ms=9000,
            end_offset_ms=12500,
            text="Of course. I'll update the team and share the status report tomorrow.",
            audio_uri='https://example.com/audio/employee_confirm_handover.mp3',
            ai_emotion='assuring',
            created_at=datetime.now(UTC),
        ),
        # Session 6
        SessionTurn(
            id=uuid4(),
            session_id=sessions[5].id,
            speaker=SpeakerType.user,
            start_offset_ms=0,
            end_offset_ms=3500,
            text='I noticed the budget forecast is still pending. Any update?',
            audio_uri='https://example.com/audio/manager_check_budget.mp3',
            ai_emotion='concerned',
            created_at=datetime.now(UTC),
        ),
        SessionTurn(
            id=uuid4(),
            session_id=sessions[5].id,
            speaker=SpeakerType.assistant,
            start_offset_ms=3500,
            end_offset_ms=7000,
            text="Apologies for the delay. I'll finalize it by this afternoon.",
            audio_uri='https://example.com/audio/employee_apology_budget.mp3',
            ai_emotion='apologetic',
            created_at=datetime.now(UTC),
        ),
        SessionTurn(
            id=uuid4(),
            session_id=sessions[5].id,
            speaker=SpeakerType.user,
            start_offset_ms=7000,
            end_offset_ms=10500,
            text="Alright, please prioritize it. We're presenting it tomorrow.",
            audio_uri='https://example.com/audio/manager_instruction_prioritize.mp3',
            ai_emotion='urgent',
            created_at=datetime.now(UTC),
        ),
        SessionTurn(
            id=uuid4(),
            session_id=sessions[5].id,
            speaker=SpeakerType.assistant,
            start_offset_ms=10500,
            end_offset_ms=13800,
            text="Understood. I'll share it with you before the end of the day.",
            audio_uri='https://example.com/audio/employee_confirm_budget.mp3',
            ai_emotion='committed',
            created_at=datetime.now(UTC),
        ),
        # Session 7
        SessionTurn(
            id=uuid4(),
            session_id=sessions[6].id,
            speaker=SpeakerType.user,
            start_offset_ms=0,
            end_offset_ms=3500,
            text='I noticed the budget forecast is still pending. Any update?',
            audio_uri='https://example.com/audio/manager_check_budget.mp3',
            ai_emotion='concerned',
            created_at=datetime.now(UTC),
        ),
        SessionTurn(
            id=uuid4(),
            session_id=sessions[6].id,
            speaker=SpeakerType.assistant,
            start_offset_ms=3500,
            end_offset_ms=7000,
            text="Apologies for the delay. I'll finalize it by this afternoon.",
            audio_uri='https://example.com/audio/employee_apology_budget.mp3',
            ai_emotion='apologetic',
            created_at=datetime.now(UTC),
        ),
        SessionTurn(
            id=uuid4(),
            session_id=sessions[6].id,
            speaker=SpeakerType.user,
            start_offset_ms=7000,
            end_offset_ms=10500,
            text="Alright, please prioritize it. We're presenting it tomorrow.",
            audio_uri='https://example.com/audio/manager_instruction_prioritize.mp3',
            ai_emotion='urgent',
            created_at=datetime.now(UTC),
        ),
        SessionTurn(
            id=uuid4(),
            session_id=sessions[6].id,
            speaker=SpeakerType.assistant,
            start_offset_ms=10500,
            end_offset_ms=13800,
            text="Understood. I'll share it with you before the end of the day.",
            audio_uri='https://example.com/audio/employee_confirm_budget.mp3',
            ai_emotion='committed',
            created_at=datetime.now(UTC),
        ),
        # Session 8
        SessionTurn(
            id=uuid4(),
            session_id=sessions[7].id,
            speaker=SpeakerType.user,
            start_offset_ms=0,
            end_offset_ms=3500,
            text='I noticed the budget forecast is still pending. Any update?',
            audio_uri='https://example.com/audio/manager_check_budget.mp3',
            ai_emotion='concerned',
            created_at=datetime.now(UTC),
        ),
        SessionTurn(
            id=uuid4(),
            session_id=sessions[7].id,
            speaker=SpeakerType.assistant,
            start_offset_ms=3500,
            end_offset_ms=7000,
            text="Apologies for the delay. I'll finalize it by this afternoon.",
            audio_uri='https://example.com/audio/employee_apology_budget.mp3',
            ai_emotion='apologetic',
            created_at=datetime.now(UTC),
        ),
        SessionTurn(
            id=uuid4(),
            session_id=sessions[7].id,
            speaker=SpeakerType.user,
            start_offset_ms=7000,
            end_offset_ms=10500,
            text="Alright, please prioritize it. We're presenting it tomorrow.",
            audio_uri='https://example.com/audio/manager_instruction_prioritize.mp3',
            ai_emotion='urgent',
            created_at=datetime.now(UTC),
        ),
        SessionTurn(
            id=uuid4(),
            session_id=sessions[7].id,
            speaker=SpeakerType.assistant,
            start_offset_ms=10500,
            end_offset_ms=13800,
            text="Understood. I'll share it with you before the end of the day.",
            audio_uri='https://example.com/audio/employee_confirm_budget.mp3',
            ai_emotion='committed',
            created_at=datetime.now(UTC),
        ),
    ]


def get_dummy_sessions(conversation_scenarios: list[ConversationScenario]) -> list[Session]:
    return [
        Session(
            id=UUID('4e5174f9-78da-428c-bb9f-4556a14163cc'),
            scenario_id=conversation_scenarios[0].id,
            scheduled_at=datetime.now(UTC),
            started_at=datetime.now(UTC),
            ended_at=datetime.now(UTC),
            status=SessionStatus.completed,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        ),
        Session(
            id=uuid4(),
            scenario_id=conversation_scenarios[1].id,
            scheduled_at=datetime.now(UTC),
            started_at=datetime.now(UTC),
            ended_at=datetime.now(UTC),
            status=SessionStatus.completed,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        ),
        Session(
            id=uuid4(),
            scenario_id=conversation_scenarios[1].id,
            scheduled_at=datetime.now(UTC),
            started_at=datetime.now(UTC),
            ended_at=datetime.now(UTC),
            status=SessionStatus.completed,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        ),
        Session(
            id=uuid4(),
            scenario_id=conversation_scenarios[1].id,
            scheduled_at=datetime.now(UTC),
            started_at=datetime.now(UTC),
            ended_at=datetime.now(UTC),
            status=SessionStatus.completed,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        ),
        Session(
            id=uuid4(),
            scenario_id=conversation_scenarios[2].id,
            scheduled_at=datetime.now(UTC),
            started_at=datetime.now(UTC),
            ended_at=datetime.now(UTC),
            status=SessionStatus.completed,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        ),
        Session(
            id=uuid4(),
            scenario_id=conversation_scenarios[3].id,
            scheduled_at=datetime.now(UTC),
            started_at=datetime.now(UTC),
            ended_at=datetime.now(UTC),
            status=SessionStatus.completed,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        ),
        Session(
            id=uuid4(),
            scenario_id=conversation_scenarios[2].id,
            scheduled_at=datetime.now(UTC),
            started_at=datetime.now(UTC),
            ended_at=datetime.now(UTC),
            status=SessionStatus.completed,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        ),
        Session(
            id=uuid4(),
            scenario_id=conversation_scenarios[3].id,
            scheduled_at=datetime.now(UTC),
            started_at=datetime.now(UTC),
            ended_at=datetime.now(UTC),
            status=SessionStatus.completed,
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
            scores={'structure': 4, 'empathy': 5, 'focus': 4, 'clarity': 4},
            tone_analysis={'positive': 70, 'neutral': 20, 'negative': 10},
            overall_score=4.3,
            transcript_uri='',
            full_audio_filename='8eda3a5b-0d87-4435-a7a3-d274f11febfa.mp3',
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
            status=FeedbackStatus.completed,  # Use the enum for status
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        ),
        SessionFeedback(
            id=uuid4(),
            session_id=sessions[1].id,  # Link to the second session
            scores={'structure': 3, 'empathy': 4, 'focus': 5, 'clarity': 4},
            tone_analysis={'positive': 80, 'neutral': 15, 'negative': 5},
            overall_score=4.0,
            transcript_uri='',
            full_audio_filename='8eda3a5b-0d87-4435-a7a3-d274f11febfa.mp3',
            document_names=[
                'Communication at Work',
                'Teamwork: An Open Access Practical Guide',
                'Psychology of Human Relations',
            ],
            speak_time_percent=55.0,
            questions_asked=7,
            session_length_s=2000,
            goals_achieved=[
                'Align on team roles',
                'Set expectations for communication',
            ],
            example_positive=[
                {
                    'heading': 'Clear framing of the issue',
                    'feedback': (
                        'You effectively communicated the specific issue (missed deadlines) and its'
                        ' impact on the team without being accusatory.'
                    ),
                    'quote': (
                        "I've noticed that several deadlines were missed last week, and it's "
                        'causing our team to fall behind on the overall project timeline.'
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
            status=FeedbackStatus.completed,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        ),
        SessionFeedback(
            id=uuid4(),
            session_id=sessions[2].id,  # Link to the third session
            scores={'structure': 5, 'empathy': 4, 'focus': 3, 'clarity': 4},
            tone_analysis={'positive': 80, 'neutral': 15, 'negative': 5},
            overall_score=4.0,
            transcript_uri='',
            full_audio_filename='8eda3a5b-0d87-4435-a7a3-d274f11febfa.mp3',
            document_names=[
                'Communication at Work',
                'Teamwork: An Open Access Practical Guide',
                'Psychology of Human Relations',
            ],
            speak_time_percent=55.0,
            questions_asked=7,
            session_length_s=2000,
            goals_achieved=[
                'Align on team roles',
                'Set expectations for communication',
            ],
            example_positive=[
                {
                    'heading': 'Clear framing of the issue',
                    'feedback': (
                        'You effectively communicated the specific issue (missed deadlines) and its'
                        ' impact on the team without being accusatory.'
                    ),
                    'quote': (
                        "I've noticed that several deadlines were missed last week, and it's "
                        'causing our team to fall behind on the overall project timeline.'
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
            status=FeedbackStatus.completed,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        ),
        SessionFeedback(
            id=uuid4(),
            session_id=sessions[3].id,  # Link to the fourth session
            scores={'structure': 4, 'empathy': 3, 'focus': 5, 'clarity': 4},
            tone_analysis={'positive': 80, 'neutral': 15, 'negative': 5},
            overall_score=4.0,
            transcript_uri='',
            full_audio_filename='8eda3a5b-0d87-4435-a7a3-d274f11febfa.mp3',
            document_names=[
                'Communication at Work',
            ],
            speak_time_percent=55.0,
            questions_asked=7,
            session_length_s=2000,
            goals_achieved=[
                'Maintain professionalism',
                'Provide specific feedback',
                'Foster mutual understanding',
                'End on a positive note',
            ],
            example_positive=[
                {
                    'heading': 'Clear framing of the issue',
                    'feedback': (
                        'You effectively communicated the specific issue (missed deadlines) and its'
                        ' impact on the team without being accusatory.'
                    ),
                    'quote': (
                        "I've noticed that several deadlines were missed last week, and it's "
                        'causing our team to fall behind on the overall project timeline.'
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
            status=FeedbackStatus.completed,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        ),
        SessionFeedback(
            id=uuid4(),
            session_id=sessions[4].id,  # Link to the fifth session
            scores={'structure': 5, 'empathy': 5, 'focus': 4, 'clarity': 5},
            tone_analysis={'positive': 70, 'neutral': 20, 'negative': 10},
            overall_score=4.8,
            transcript_uri='',
            full_audio_filename='8eda3a5b-0d87-4435-a7a3-d274f11febfa.mp3',
            document_names=[
                'Communication at Work',
                'Teamwork: An Open Access Practical Guide',
                'Psychology of Human Relations',
            ],
            speak_time_percent=60.5,
            questions_asked=5,
            session_length_s=1800,
            goals_achieved=[
                'Bring clarity to the situation',
                'Encourage open dialogue',
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
            status=FeedbackStatus.completed,  # Use the enum for status
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        ),
        SessionFeedback(
            id=uuid4(),
            session_id=sessions[5].id,  # Link to the first session
            scores={'structure': 4, 'empathy': 3, 'focus': 4, 'clarity': 4},
            tone_analysis={'positive': 70, 'neutral': 20, 'negative': 10},
            overall_score=3.8,
            transcript_uri='',
            full_audio_filename='8eda3a5b-0d87-4435-a7a3-d274f11febfa.mp3',
            document_names=[
                'Communication at Work',
                'Psychology of Human Relations',
            ],
            speak_time_percent=60.5,
            questions_asked=5,
            session_length_s=1800,
            goals_achieved=[
                'Bring clarity to the situation',
                'Encourage open dialogue',
                'Maintain professionalism',
                'Provide specific feedback',
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
            status=FeedbackStatus.completed,  # Use the enum for status
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        ),
        SessionFeedback(
            id=uuid4(),
            session_id=sessions[6].id,  # Link to the first session
            scores={'structure': 4, 'empathy': 3, 'focus': 4, 'clarity': 4},
            tone_analysis={'positive': 70, 'neutral': 20, 'negative': 10},
            overall_score=3.8,
            transcript_uri='',
            full_audio_filename='8eda3a5b-0d87-4435-a7a3-d274f11febfa.mp3',
            document_names=[
                'Communication at Work',
                'Teamwork: An Open Access Practical Guide',
                'Psychology of Human Relations',
            ],
            speak_time_percent=60.5,
            questions_asked=5,
            session_length_s=1800,
            goals_achieved=['Bring clarity to the situation'],
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
            status=FeedbackStatus.completed,  # Use the enum for status
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        ),
        SessionFeedback(
            id=uuid4(),
            session_id=sessions[7].id,  # Link to the first session
            scores={'structure': 4, 'empathy': 3, 'focus': 4, 'clarity': 4},
            tone_analysis={'positive': 70, 'neutral': 20, 'negative': 10},
            overall_score=3.8,
            transcript_uri='',
            full_audio_filename='8eda3a5b-0d87-4435-a7a3-d274f11febfa.mp3',
            document_names=[
                'Psychology of Human Relations',
            ],
            speak_time_percent=60.5,
            questions_asked=5,
            session_length_s=1800,
            goals_achieved=['Bring clarity to the situation'],
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
            status=FeedbackStatus.completed,  # Use the enum for status
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
                'Bring clarity to the situation',
                'Encourage open dialogue',
                'Maintain professionalism',
                'Provide specific feedback',
                'Foster mutual understanding',
                'End on a positive note',
            ],
            document_names=[
                'Communication at Work',
                'Teamwork: An Open Access Practical Guide',
                'Psychology of Human Relations',
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
                'Align on team roles',
                'Set expectations for communication',
                'Identify potential risks',
            ],
            document_names=['Communication at Work', 'Giving Feedback'],
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
        ScenarioPreparation(
            id=uuid4(),
            scenario_id=conversation_scenarios[2].id,
            objectives=[
                'Bring clarity to the situation',
                'Encourage open dialogue',
                'Maintain professionalism',
                'Align on team roles',
                'Set expectations for communication',
            ],
            document_names=[
                'Psychology of Human Relations',
                'Teamwork: An Open Access Practical Guide',
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
            scenario_id=conversation_scenarios[3].id,
            document_names=['Communication at Work', 'A Guide to Effective Negotiations'],
            objectives=[
                'Bring clarity to the situation',
                'Encourage open dialogue',
                'Maintain professionalism',
                'Provide specific feedback',
                'Foster mutual understanding',
                'End on a positive note',
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
            score_sum=34533 * 3.5,
        )
    ]


def get_mock_user_data() -> tuple[AdminUserAttributes, AdminUserAttributes]:
    """
    Generate mock user data for testing purposes.
    """
    return (
        {
            'id': MockUserIdsEnum.USER.value.__str__(),
            'email': settings.mock_user_data.email,
            'password': settings.mock_user_data.password,
            'phone': settings.mock_user_data.phone,
            'email_confirm': True,
            'phone_confirm': True,
            'user_metadata': {
                'full_name': settings.mock_user_data.full_name,
            },
        },
        {
            'id': MockUserIdsEnum.ADMIN.value.__str__(),
            'email': settings.mock_admin_data.email,
            'password': settings.mock_admin_data.password,
            'phone': settings.mock_admin_data.phone,
            'email_confirm': True,
            'phone_confirm': True,
            'user_metadata': {
                'full_name': settings.mock_admin_data.full_name,
            },
        },
    )


def get_dummy_live_feedback_data(session_turns: list[SessionTurn]) -> list[LiveFeedback]:
    return [
        LiveFeedback(
            id=uuid4(),
            session_id=session_turns[0].session_id,
            heading='Tone',
            feedback_text='Speak more calmly',
            created_at=datetime.now(UTC),
        ),
        LiveFeedback(
            id=uuid4(),
            session_id=session_turns[1].session_id,
            heading='Content',
            feedback_text='Use concrete facts for the employee underperforming',
            created_at=datetime.now(UTC),
        ),
    ]


def create_mock_users() -> None:
    attributes, admin_attributes = get_mock_user_data()

    supabase = get_supabase_client()

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
    supabase = get_supabase_client()

    for user_id in [MockUserIdsEnum.USER.value, MockUserIdsEnum.ADMIN.value]:
        try:
            supabase.auth.admin.delete_user(user_id.__str__())
        except AuthError as e:
            if e.code != 'user_not_found':
                raise e
        except Exception as e:
            raise e
