from uuid import UUID

from pydantic import BaseModel


class ConnectedAccountDTO(BaseModel):
    id: UUID

    provider_identifier: str
    messagesubscription:bool


class ChannelResponseDTO(BaseModel):
    id: UUID
    code: str
    name: str

    connection_status: str

    connected_accounts: list[ConnectedAccountDTO] = []
