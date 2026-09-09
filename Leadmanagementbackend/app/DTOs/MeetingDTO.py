from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class CreateMeetingDTO(BaseModel):
    lead_id: UUID
    channel_connection_id: UUID

    title: str = Field(
        min_length=1,
        max_length=255,
    )

    description: str | None = None

    start_time: datetime
    end_time: datetime


class MeetingResponseDTO(BaseModel):
    id: UUID
    lead_id: UUID
    channel_connection_id: UUID

    provider_event_id: str
    title: str
    description: str | None

    start_time: datetime
    end_time: datetime

    meeting_link: str | None
    status: str

    class Config:
        from_attributes = True

class UpdateMeetingDTO(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    description: str | None = None

    start_time: datetime | None = None

    end_time: datetime | None = None