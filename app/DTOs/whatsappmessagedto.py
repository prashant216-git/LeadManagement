from pydantic import BaseModel


class SendMessageDTO(BaseModel):
    user_id: int
    draft_id: int
    message: str