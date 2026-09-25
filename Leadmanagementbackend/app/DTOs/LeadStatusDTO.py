from uuid import UUID

from pydantic import BaseModel


class LeadStatusCreateDTO(BaseModel):
    status_name: str | None = None
    is_active: bool | None = None
    is_default: bool | None = None
    colour: str | None = None



class LeadStatusUpdateDTO(BaseModel):
    status_name: str | None = None
    is_active: bool | None = None
    is_default: bool | None = None
    colour : str | None = None


class LeadStatusResponseDTO(BaseModel):
    id: UUID
    user_id: UUID
    status_name: str
    is_active: bool
    is_default: bool
    colour: str | None
    created_by: UUID

    class Config:
        from_attributes = True




class ChangeLeadStatusDTO(BaseModel):
    lead_id: UUID | None = None
    status_id: UUID | None = None