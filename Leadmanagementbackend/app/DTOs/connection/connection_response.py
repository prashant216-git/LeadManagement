from typing import Optional

from pydantic import BaseModel


class ConnectResponse(BaseModel):
    success: bool
    authorization_url: Optional[str] = None
    config_id: Optional[str] = None
    message: str
    state: Optional[str] = None