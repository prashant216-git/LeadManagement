from datetime import datetime

from pydantic import BaseModel, Field


class Leadetails(BaseModel):
    connection_id:int | None=None
    source_identifier:str | None=None
    id: int
    name: str | None = None
    email: str | None = None
    phone_number: str | None = None
    created_at: datetime | None = None


class LeadlistDTO(BaseModel):
    channel_id: int | None=None
    Leaddetails: list[Leadetails] = Field(
        default_factory=list
    )

    page: int
    page_size: int
    total: int
    total_pages: int