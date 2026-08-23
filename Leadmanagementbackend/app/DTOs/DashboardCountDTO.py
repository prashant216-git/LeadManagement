from pydantic import BaseModel


class DashboardCountDTO(BaseModel):
    tenant_id: int
    today_leads: int
    monthly_leads: int
    total_leads: int