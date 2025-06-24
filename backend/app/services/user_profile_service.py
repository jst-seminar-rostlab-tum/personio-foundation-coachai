from typing import Annotated

from fastapi import Depends, HTTPException
from sqlmodel import Session as DBSession
from supabase import AuthError

from app.database import get_db_session, supabase
from app.models.user_profile import UserProfile


def delete_supabase_user(user_id: str) -> None:
    try:
        supabase.auth.admin.delete_user(user_id.__str__())
    except AuthError as e:
        if e.code != 'user_not_found':
            raise e
    except Exception as e:
        raise e


def delete_user_profile(
    user_id: str, db_session: Annotated[DBSession, Depends(get_db_session)]
) -> None:
    user_profile = db_session.get(UserProfile, user_id)
    if not user_profile:
        raise HTTPException(status_code=404, detail='User profile not found')
    db_session.delete(user_profile)
    db_session.commit()
