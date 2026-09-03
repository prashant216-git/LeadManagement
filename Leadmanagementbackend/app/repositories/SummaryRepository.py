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

    async def get_by_lead_id(
        self,
        lead_id: UUID,
    ) -> Summary | None:

        statement = (
            select(Summary)
            .where(Summary.lead_id == lead_id)
        )

        result = await self.db.execute(statement)

        return result.scalar_one_or_none()

    async def create(
        self,
        summary: Summary,
    ) -> Summary:

        self.db.add(summary)

        await self.db.flush()

        return summary

    async def update(
        self,
        summary: Summary,
    ) -> Summary:

        self.db.add(summary)

        await self.db.flush()

        return summary