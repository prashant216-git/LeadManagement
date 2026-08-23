from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import func, select

from app.models.Leads import Lead


class DashboardRepository:

    def __init__(self, db):
        self.db = db

    def get_lead_counts(
        self,
        user_id: UUID,
    ):

        now = datetime.now(timezone.utc)

        start_today = now.replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )

        start_month = now.replace(
            day=1,
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )

        statement = select(
            func.count(Lead.id).label(
                "total_leads"
            ),

            func.count(Lead.id).filter(
                Lead.created_at >= start_today
            ).label(
                "today_leads"
            ),

            func.count(Lead.id).filter(
                Lead.created_at >= start_month
            ).label(
                "monthly_leads"
            ),
        ).where(
            Lead.user_id == user_id
        )

        result = self.db.execute(
            statement
        )

        return result.one()