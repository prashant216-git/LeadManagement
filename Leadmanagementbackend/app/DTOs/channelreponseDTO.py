from pydantic import BaseModel
from typing import Optional, Any


class ChannelResponseDTO(BaseModel):
    id: int
    code: str
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None

    configuration_schema: Optional[dict[str, Any]] = None

    model_config = {
        "from_attributes": True
    }