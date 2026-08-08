from pydantic import BaseModel


class ConnectResponse(BaseModel):

    success: bool

    authorization_url: str | None = None

    message: str