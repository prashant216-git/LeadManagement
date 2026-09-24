from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from enums.message import QuickMessageType


class QuickMessageAttachmentDTO:



    class Response(BaseModel):
        id: UUID

        message_text: str | None = None
        title: str | None = None
        attachment_url: str | None = None
        attachment_type: QuickMessageType
        is_active: bool


        model_config = ConfigDict(from_attributes=True)