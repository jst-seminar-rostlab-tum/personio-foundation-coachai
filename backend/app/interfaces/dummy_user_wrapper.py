from dataclasses import dataclass

from gotrue import AdminUserAttributes

from app.models import UserProfile


@dataclass
class DummyUserWrapper:
    user_profile: UserProfile
    supabase_profile: AdminUserAttributes
