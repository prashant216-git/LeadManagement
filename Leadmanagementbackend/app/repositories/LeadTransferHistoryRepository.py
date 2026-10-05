from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.models.LeadTransferHistory import LeadTransferHistory
from app.enums.LeadTransfer import (
    LeadTransferStatus,
)


class LeadTransferHistoryRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    # --------------------------------------------------
    # CREATE
    # --------------------------------------------------

    def create(
        self,
        transfer: LeadTransferHistory,
    ) -> LeadTransferHistory:

        self.db.add(transfer)
        self.db.flush()

        self.db.commit()
        self.db.refresh(transfer)

        return transfer

    # --------------------------------------------------
    # GET BY ID
    # --------------------------------------------------

    def get_by_id(
        self,
        transfer_id: UUID,
    ) -> LeadTransferHistory | None:

        statement = (
            select(LeadTransferHistory)
            .where(
                LeadTransferHistory.id == transfer_id
            )
        )

        return self.db.execute(statement).scalar_one_or_none()

    # --------------------------------------------------
    # GET ALL TRANSFERS FOR LEAD
    # --------------------------------------------------

    def get_by_lead_id(
        self,
        lead_id: UUID,
    ) -> list[LeadTransferHistory]:

        statement = (
            select(LeadTransferHistory)
            .where(
                LeadTransferHistory.lead_id == lead_id
            )
            .order_by(
                LeadTransferHistory.created_at.desc()
            )
        )

        result = self.db.execute(statement)

        return list(result.scalars().all())

    # --------------------------------------------------
    # GET TRANSFERS IN
    # --------------------------------------------------
    # User received the lead

    def get_transferred_in(
        self,
        user_id: UUID,
    ) -> list[LeadTransferHistory]:

        statement = (
            select(LeadTransferHistory)
            .where(
                LeadTransferHistory.transfer_to == user_id
            )
            .order_by(
                LeadTransferHistory.created_at.desc()
            )
        )

        result = self.db.execute(statement)

        return list(result.scalars().all())

    # --------------------------------------------------
    # GET TRANSFERS OUT
    # --------------------------------------------------
    # User transferred the lead to somebody else

    def get_transferred_out(
        self,
        user_id: UUID,
    ) -> list[LeadTransferHistory]:

        statement = (
            select(LeadTransferHistory)
            .where(
                LeadTransferHistory.transfer_from == user_id
            )
            .order_by(
                LeadTransferHistory.created_at.desc()
            )
        )

        result = self.db.execute(statement)

        return list(result.scalars().all())

    # --------------------------------------------------
    # GET ACTIVE / COMPLETED TRANSFERS FOR LEAD
    # --------------------------------------------------

    def get_completed_by_lead_id(
        self,
        lead_id: UUID,
    ) -> list[LeadTransferHistory]:

        statement = (
            select(LeadTransferHistory)
            .where(
                LeadTransferHistory.lead_id == lead_id,
                LeadTransferHistory.transfer_status
                == LeadTransferStatus.COMPLETED,
            )
            .order_by(
                LeadTransferHistory.created_at.desc()
            )
        )

        result = self.db.execute(statement)

        return list(result.scalars().all())

    # --------------------------------------------------
    # GET LATEST TRANSFER
    # --------------------------------------------------

    def get_latest_by_lead_id(
        self,
        lead_id: UUID,
    ) -> LeadTransferHistory | None:

        statement = (
            select(LeadTransferHistory)
            .where(
                LeadTransferHistory.lead_id == lead_id
            )
            .order_by(
                LeadTransferHistory.created_at.desc()
            )
            .limit(1)
        )

        return self.db.execute(
            statement
        ).scalar_one_or_none()

    # --------------------------------------------------
    # UPDATE STATUS
    # --------------------------------------------------

    def update_status(
        self,
        transfer_id: UUID,
        status: LeadTransferStatus,
        updated_by: UUID,
    ) -> LeadTransferHistory | None:

        statement = (
            update(LeadTransferHistory)
            .where(
                LeadTransferHistory.id == transfer_id
            )
            .values(
                transfer_status=status,
                updated_by=updated_by,
            )
            .returning(LeadTransferHistory)
        )

        result = self.db.execute(statement)

        transfer = result.scalar_one_or_none()

        return transfer