from pydantic import BaseModel


class Attachment(BaseModel):
    filename: str
    content_type: str
    url: str | None = None