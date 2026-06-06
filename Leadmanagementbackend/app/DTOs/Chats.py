from pydantic import BaseModel


class ChatSidebarDTO(BaseModel):
    user_id: int
    name: str | None = None
    phone_number: str | None = None
    email: str | None = None
    latest_message: str | None = None
    latest_message_time: str | None = None