from pydantic import BaseModel


class MeetingAvailabilityDTO(BaseModel):
    available: bool