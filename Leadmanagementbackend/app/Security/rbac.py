from collections import defaultdict

import httpx
from fastapi import HTTPException, status

from app.core.config import settings
from app.Security.schema import (
    RBACResponse,
    CurrentUser,
)


class RBACService:

    def __init__(self):
        self.base_url = settings.RBAC_SERVICE_URL

    # ==================================================
    # RBAC API
    # ==================================================

    async def get_user_details(
        self,
        token: str,
    ) -> RBACResponse:

        try:

            async with httpx.AsyncClient(
                timeout=10.0
            ) as client:
                print(token)

                response = await client.get(
                    f"{self.base_url}/api/organization/user/self",
                    headers={
                        "Authorization": f"Bearer {token}"
                    },
                )

            if response.status_code == 401:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials",
                )

            response.raise_for_status()

            return RBACResponse.model_validate(
                response.json()
            )

        except HTTPException:
            raise

        except httpx.TimeoutException:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="RBAC service timeout",
            )

        except httpx.HTTPError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,

                detail=f"RBAC service unavailable: {exc}",
            )

    # ==================================================
    # Extract Permissions
    # ==================================================

    def extract_permissions(
        self,
        rbac: RBACResponse,
    ) -> dict[str, set[str]]:

        permissions = defaultdict(set)

        for role in rbac.roles:

            for permission in role.permissions:

                permission_name = (
                    permission.permissionName.upper()
                )

                for privilege in permission.privileges:

                    permissions[
                        permission_name
                    ].add(
                        privilege.privilegeName.upper()
                    )

        return dict(permissions)

    # ==================================================
    # Build Current User
    # ==================================================

    def build_current_user(
        self,
        rbac: RBACResponse,
    ) -> CurrentUser:

        permissions = self.extract_permissions(
            rbac
        )

        return CurrentUser(
            user_id=rbac.userId,
            email=rbac.userEmail,
            name=rbac.name,
            client_id=rbac.clientId,
            permissions=permissions,
        )

    # ==================================================
    # Get Current User
    # ==================================================

    async def get_current_user(
        self,
        token: str,
    ) -> CurrentUser:

        rbac = await self.get_user_details(
            token
        )

        return self.build_current_user(
            rbac
        )

    # ==================================================
    # Check Privilege
    # ==================================================

    def has_privilege(
        self,
        permissions: dict[str, set[str]],
        permission: str,
        privilege: str,
    ) -> bool:

        permission = permission.upper()
        privilege = privilege.upper()

        return privilege in permissions.get(
            permission,
            set(),
        )

    # ==================================================
    # Require Privilege
    # ==================================================

    def require_privilege(
        self,
        permissions: dict[str, set[str]],
        permission: str,
        privilege: str,
    ) -> None:

        if not self.has_privilege(
            permissions=permissions,
            permission=permission,
            privilege=privilege,
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"Missing privilege "
                    f"{permission.upper()}:"
                    f"{privilege.upper()}"
                ),
            )


rbac_service = RBACService()