from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.models.lead_status_master import LeadStatusMaster


class LeadStatusMasterRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    def get_by_user_id(
        self,
        user_id: UUID,
    ) -> list[LeadStatusMaster]:

        statement = (
            select(LeadStatusMaster)
            .where(
                LeadStatusMaster.user_id == user_id
            )
            .order_by(
                LeadStatusMaster.created_at.asc()
            )
        )

        result = self.db.execute(statement)

        return list(result.scalars().all())

    def get_by_user_id_default(
        self,
        user_id: UUID,
    ) -> list[LeadStatusMaster]:

        statement = (
            select(LeadStatusMaster)
            .where(
                LeadStatusMaster.user_id == user_id,LeadStatusMaster.is_default == True
            )
            .order_by(
                LeadStatusMaster.created_at.asc()
            )
        )

        result = self.db.execute(statement)

        return result.scalar_one_or_none()

    def save(
        self,
        status: LeadStatusMaster,
    ) -> LeadStatusMaster:

        self.db.add(status)
        self.db.flush()
        self.db.commit()
        self.db.refresh(status)

        return status