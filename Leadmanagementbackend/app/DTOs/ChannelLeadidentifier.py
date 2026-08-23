from pydantic import BaseModel


class ChannelIdentifierDTO(BaseModel):

    connection_id: int

    identifier: str | None = None

    display_name: str | None = None

    is_lead_connection: bool = False


class LeadChannelIdentifiersDTO(BaseModel):

    lead_id: int

    channel_id: int

    identifiers: list[ChannelIdentifierDTO] = []