

from pydantic import BaseModel, Field

class SendMessageDTO(BaseModel):

    lead_id: int

    channel_id: int

    identifier: str

    content: str

    reply_to_message_id: int | None = None