from pydantic import BaseModel


class SendMessageResponse(BaseModel):

    success: bool

    provider_message_id: str | None = None

    message: str | None = None