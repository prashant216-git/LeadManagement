from uuid import UUID

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
        user_id: UUID,
    ) -> DashboardCountDTO:

        result = (
            self.dashboard_repository
            .get_lead_counts(
                user_id=user_id
            )
        )

        return DashboardCountDTO(
            user_id=user_id,
            today_leads=result.today_leads,
            monthly_leads=result.monthly_leads,
            total_leads=result.total_leads,
        )