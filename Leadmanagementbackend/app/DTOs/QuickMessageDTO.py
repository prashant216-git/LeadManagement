from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.enums.message import QuickMessageType


class QuickMessageResponse(BaseModel):
    id: UUID

    message_text: str | None = None
    title: str | None = None
    attachment_type: QuickMessageType
    is_active: bool

    attachment_urls: list[str] | None = None

class ListResponse(BaseModel):
    items: list[QuickMessageResponse]


class QuickMessageCreate(BaseModel):
    message_text: str
    title: str
    attachment_type: QuickMessageType = QuickMessageType.TEXT,
    attachment_ids: list[UUID] | None = None,