from uuid import UUID

from pydantic import BaseModel


class ChannelIdentifierDTO(BaseModel):

    connection_id: UUID

    identifier: str | None = None

    display_name: str | None = None

    is_lead_connection: bool = False


class LeadChannelIdentifiersDTO(BaseModel):

    lead_id: UUID

    channel_id: UUID

    identifiers: list[ChannelIdentifierDTO] = []