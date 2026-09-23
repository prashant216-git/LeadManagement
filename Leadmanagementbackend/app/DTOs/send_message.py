from uuid import UUID

from pydantic import BaseModel, Field

class SendMessageDTO(BaseModel):

    lead_id: UUID

    channel_id: UUID

    connection_id: UUID

    content: str

    reply_to_message_id: UUID | None = None