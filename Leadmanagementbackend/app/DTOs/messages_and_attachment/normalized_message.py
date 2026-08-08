from datetime import datetime

from pydantic import BaseModel


class NormalizedMessage(BaseModel):

    provider_message_id: str

    sender: str

    recipient: str

    message: str

    timestamp: datetime