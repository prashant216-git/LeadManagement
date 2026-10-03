from fastapi import Depends
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)

from app.Security.rbac import rbac_service
from app.Security.schema import CurrentUser


bearer_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(
        bearer_scheme
    ),
) -> CurrentUser:

    print(credentials.credentials)

    return await rbac_service.get_current_user(
        credentials.credentials
    )