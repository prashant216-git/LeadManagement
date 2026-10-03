from uuid import UUID

from pydantic import BaseModel


class Privilege(BaseModel):
    privilegeId: UUID
    privilegeName: str


class Permission(BaseModel):
    permissionId: UUID
    permissionName: str
    categoryId: UUID
    categoryName: str
    privileges: list[Privilege]


class Role(BaseModel):
    roleId: UUID
    roleName: str
    roleDescription: str | None = None
    permissions: list[Permission]


class RBACResponse(BaseModel):
    clientId: UUID | None = None
    clientName: str | None = None
    clientEmail: str | None = None
    clientAddress: str | None = None
    clientStatus: str | None = None

    roleName: str | None = None

    userId: UUID
    userEmail: str
    name: str
    userActive: int

    roles: list[Role]




class CurrentUser(BaseModel):
    user_id: UUID
    email: str
    name: str
    client_id: UUID | None = None
    permissions: dict[str, set[str]]