from pydantic import BaseModel


class CreateManualLeadDTO(BaseModel):

    name: str | None = None

    email: str | None = None

    phone_number: str | None = None