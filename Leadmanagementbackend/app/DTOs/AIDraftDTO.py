# app/DTOs/DraftDTO.py

from pydantic import BaseModel


class DraftDTO(BaseModel):
    draft_id: int
    user_id: int
    message_id: int
    draft_text: str
    status: str