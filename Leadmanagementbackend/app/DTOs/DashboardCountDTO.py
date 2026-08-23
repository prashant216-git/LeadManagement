from uuid import UUID

from pydantic import BaseModel


class DashboardCountDTO(BaseModel):
    user_id: UUID
    today_leads: int
    monthly_leads: int
    total_leads: int