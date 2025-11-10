from dataclasses import dataclass

from supabase_auth import AdminUserAttributes

from app.models import UserProfile


@dataclass
class DummyUserWrapper:
    user_profile: UserProfile
    supabase_profile: AdminUserAttributes
