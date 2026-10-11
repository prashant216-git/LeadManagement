from typing import List
from uuid import UUID

from fastapi import UploadFile, File
from pydantic import BaseModel, Field

class SendMessageDTO(BaseModel):

    lead_id: UUID

    subject: str | None = None
    
    connection_id: UUID

    content: str

    reply_to_message_id: UUID | None = None

    attachment_ids: list[UUID] | None = None