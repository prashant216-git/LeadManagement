from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.LeadStatusHistory import LeadStatusHistory
from app.models.lead_status_master import LeadStatusMaster


class LeadStatusHistoryRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    def create(
        self,
        lead_id: UUID,
        status_id: UUID,
        comment: str | None,
        changed_by: UUID | None,
    ) -> LeadStatusHistory:

        history = LeadStatusHistory(
            lead_id=lead_id,
            status_id=status_id,
            comment=comment,
            changed_by=changed_by,
        )

        self.db.add(history)

        self.db.flush()
        self.db.commit()
        self.db.refresh(history)


        return history

    def get_history_by_lead_id(
            self,
            lead_id: int,
    ) -> list[LeadStatusHistory]:
        result = self.db.execute(
            select(LeadStatusHistory,LeadStatusMaster)
            .join(
                LeadStatusMaster,
                LeadStatusHistory.status_id == LeadStatusMaster.id,
            )
            .where(
                LeadStatusHistory.lead_id == lead_id
            )
            .order_by(
                LeadStatusHistory.created_at.desc()
            )
        )

        return result.all()

    def get_by_lead(
        self,
        lead_id: int,
    ) -> list[LeadStatusHistory]:

        result = self.db.execute(
            select(LeadStatusHistory)
            .where(
                LeadStatusHistory.lead_id == lead_id
            )
            .order_by(
                LeadStatusHistory.created_at.desc()
            )
        )

        return list(result.scalars().all())