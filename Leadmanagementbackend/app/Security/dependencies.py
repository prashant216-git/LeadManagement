from fastapi import Depends, HTTPException, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)

from app.repositories.Userrepositories import UserRepository
from app.Security.jwtservice import JWTService
from app.Security.schema import CurrentUser
from app.dependencies.repositories import (
    get_user_repository,
)


bearer_scheme = HTTPBearer()

jwt_service = JWTService()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(
        bearer_scheme
    ),
    user_repository: UserRepository = Depends(
        get_user_repository
    ),
) -> CurrentUser:

    try:
        payload = jwt_service.decode_token(
            credentials.credentials
        )

        user_email = payload.get("sub")

        if not user_email:
            raise ValueError(
                "User ID missing from token."
            )

        user = user_repository.get_by_gmail(
            user_email
        )

        if user is None:
            raise ValueError(
                "User does not exist."
            )

        return CurrentUser(
            id=user.id,
        )

    except Exception:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token.",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )