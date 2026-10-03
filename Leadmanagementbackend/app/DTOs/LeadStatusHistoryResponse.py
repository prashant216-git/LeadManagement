from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class LeadStatusHistoryResponse(BaseModel):
    id: UUID
    lead_id: UUID
    status_id: UUID
    status_name: str
    comment: str | None
    changed_by: UUID | None
    created_at: datetime