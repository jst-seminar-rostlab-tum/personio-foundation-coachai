from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from supabase import Client, create_client

from app.config import Settings

settings = Settings()


supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
security = HTTPBearer()


def verify_jwt(credentials: HTTPAuthorizationCredentials = Depends(security)):  # noqa: ANN201, B008
    """
    Checks the validity of the JWT token and retrieves the user information.
    """

    print(f'Verifying JWT: {credentials.credentials}')

    token = credentials.credentials
    try:
        user = supabase.auth.get_user(token)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token')

        print(f'User verified: {user}')

        return user
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e)) from e
