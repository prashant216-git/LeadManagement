# app/DTOs/DraftDTO.py
from uuid import UUID

from pydantic import BaseModel


class DraftDTO(BaseModel):
    draft_id: UUID
    message_id: UUID
    draft_text: str
    status: str
    summarytext: str | None=None