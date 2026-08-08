from pydantic import BaseModel


class ConnectRequest(BaseModel):

    redirect_uri: str | None = None