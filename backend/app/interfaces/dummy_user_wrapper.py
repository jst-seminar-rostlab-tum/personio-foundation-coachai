"""Interface helpers for dummy user wrapper."""

from dataclasses import dataclass

from supabase_auth import AdminUserAttributes

from app.models import UserProfile


@dataclass
class DummyUserWrapper:
    """Bundle a local UserProfile with a Supabase admin profile.

    Parameters:
        user_profile (UserProfile): Local user profile model.
        supabase_profile (AdminUserAttributes): Supabase admin user attributes.
    """

    user_profile: UserProfile
    supabase_profile: AdminUserAttributes
