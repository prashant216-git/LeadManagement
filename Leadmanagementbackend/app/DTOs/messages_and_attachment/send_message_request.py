from typing import Any

from pydantic import BaseModel


class SendMessageRequest(BaseModel):
    """
    Generic outbound message request.
    """

    recipient: str

    subject: str | None = None

    message: str

    attachments: list[str] = []

    metadata: dict[str, Any] = {}