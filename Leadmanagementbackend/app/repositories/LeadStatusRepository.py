from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.models.lead_status import LeadStatus


class LeadStatusRepository:

    def __init__(self, db:AsyncSession ):
        self.db = db

    def get_by_lead_id(
        self,
        lead_id: UUID,
    ) -> list[LeadStatus]:

        statement = (
            select(LeadStatus)
            .where(
                LeadStatus.lead_id == lead_id
            )
            .order_by(
                LeadStatus.created_at.asc()
            )
        )

        result = self.db.execute(statement)

        return list(result.scalars().all())

    def save(
        self,
        lead_status: LeadStatus,
    ) -> LeadStatus:

        self.db.add(lead_status)
        self.db.commit()
        self.db.refresh(lead_status)


        return lead_status