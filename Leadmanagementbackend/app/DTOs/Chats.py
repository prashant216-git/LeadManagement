from datetime import datetime

from pydantic import BaseModel


class ChatSidebarItemDTO(BaseModel):
    lead_id: int
    name: str | None = None
    email: str | None = None
    phone_number: str | None = None

    latest_message: str | None = None
    latest_message_time: datetime | None = None


class ChatSidebarDTO(BaseModel):
    channel_id: int
    chats: list[ChatSidebarItemDTO]