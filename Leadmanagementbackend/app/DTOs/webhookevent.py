from typing import Any

from pydantic import BaseModel


class WebhookEvent(BaseModel):

    event_type: str

    payload: dict[str, Any]