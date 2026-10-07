from datetime import datetime
from typing import List
from uuid import UUID

from fastapi import UploadFile, File
from pydantic import BaseModel

from app.enums.message import (
    MessageDirection,
    MessageType, ScheduledMessageStatus,
)


class MessageDetailsDTO(BaseModel):

    id: UUID

    direction: MessageDirection | None = None

    sender_identifier: str | None = None

    recipient_identifier: str | None = None

    content: str | None = None

    message_type: MessageType | None = None

    repliedmessageid: UUID | None = None

    provider_created_at: datetime | None = None

    attachment_urls: list[str] | None = None


class LeadMessagesResponseDTO(BaseModel):

    lead_id: UUID

    lead_name: str

    lead_email: str | None = None

    lead_phone: str | None = None

    messages: list[MessageDetailsDTO]







class ScheduledMessageCreate(BaseModel):

    lead_id: UUID
    channel_connection_id: UUID
    content: str
    scheduled_at: datetime
    attachment_ids: list[UUID] | None = None


class ScheduledMessageResponse(BaseModel):
    id: UUID

    lead_id: UUID
    channel_connection_id: UUID
    content: str
    scheduled_at: datetime
    status: ScheduledMessageStatus

    model_config = {
        "from_attributes": True
    }

class CancelledScheduledMessageResponse(BaseModel):
    id: UUID

    lead_id: UUID
    channel_connection_id: UUID
    content: str
    scheduled_at: datetime
    cancelled_at: datetime
    status: str

    model_config = {
        "from_attributes": True
    }