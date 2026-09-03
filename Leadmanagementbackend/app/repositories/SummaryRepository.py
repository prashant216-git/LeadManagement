from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Summary


class SummaryRepository:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    def get_by_lead_id(
        self,
        lead_id: UUID,
    ) -> Summary | None:

        statement = (
            select(Summary)
            .where(Summary.lead_id == lead_id)
        )

        result =  self.db.execute(statement)

        return result.scalar_one_or_none()

    def create(
        self,
        summary: Summary,
    ) -> Summary:

        self.db.add(summary)

        self.db.flush()

        return summary

    def update(
        self,
        summary: Summary,
    ) -> Summary:

        self.db.add(summary)

        self.db.flush()

        return summary