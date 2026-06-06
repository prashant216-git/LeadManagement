from pydantic import BaseModel

from app.DTOs.MessageDTO import MessageDTO


class UserChatDTO(BaseModel):
    user_id: int
    name: str | None = None
    phone_number: str | None = None
    email: str | None = None

    messages: list[MessageDTO]