from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.enums.message import QuickMessageType


class QuickMessageResponse(BaseModel):
    id: UUID

    message_text: str | None = None
    title: str | None = None
    attachment_type: QuickMessageType
    is_active: bool

    attachment_url: str | None = None

class ListResponse(BaseModel):
    items: list[QuickMessageResponse]