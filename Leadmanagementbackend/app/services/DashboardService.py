from app.DTOs.DashboardCountDTO import DashboardCountDTO


class DashboardService:

    def __init__(
        self,
        dashboard_repository,
    ):
        self.dashboard_repository = (
            dashboard_repository
        )

    async def get_counts(
        self,
        tenant_id: int,
    ) -> DashboardCountDTO:

        result = (
            self.dashboard_repository
            .get_lead_counts(
                tenant_id=tenant_id
            )
        )

        return DashboardCountDTO(
            tenant_id=tenant_id,
            today_leads=result.today_leads,
            monthly_leads=result.monthly_leads,
            total_leads=result.total_leads,
        )