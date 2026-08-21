from pydantic import BaseModel


class ConnectedAccountDTO(BaseModel):
    id: int

    provider_identifier: str
    messagesubscription:bool


class ChannelResponseDTO(BaseModel):
    id: int
    code: str
    name: str

    connection_status: str

    connected_accounts: list[ConnectedAccountDTO] = []
