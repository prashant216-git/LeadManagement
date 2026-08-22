from datetime import datetime

from pydantic import BaseModel

from app.enums.message import (
    MessageDirection,
    MessageType,
)


class MessageDetailsDTO(BaseModel):

    id: int

    direction: MessageDirection | None = None

    sender_identifier: str | None = None

    recipient_identifier: str | None = None

    content: str | None = None

    message_type: MessageType | None = None

    repliedmessageid: int | None = None

    provider_created_at: datetime | None = None


class LeadMessagesResponseDTO(BaseModel):

    lead_id: int

    lead_name: str

    lead_email: str | None = None

    lead_phone: str | None = None

    messages: list[MessageDetailsDTO]