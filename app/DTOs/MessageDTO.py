from pydantic import BaseModel

class MessageDTO(BaseModel):
    message: str
    sender: str
    time: str