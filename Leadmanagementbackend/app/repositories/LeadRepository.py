from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.Leads import Lead


class LeadRepository:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    # ======================================================
    # FIND LEAD
    # ======================================================

    def get_by_identifier(
        self,
            channel_connection_id:int,
        tenant_id: int,
        identifier: str,
    ):
        """
        Find a lead belonging to a tenant.

        For the current implementation the identifier
        is matched against email or phone number.
        """

        result = self.db.execute(
            select(Lead).where(
                Lead.tenant_id == tenant_id,Lead.channel_connection_id == channel_connection_id,
                (
                    (Lead.email == identifier)
                    | (Lead.phone_number == identifier)
                ),
            )
        )

        return result.scalar_one_or_none()

    # ======================================================
    # GET BY ID
    # ======================================================

    def get_by_id(
        self,
        lead_id: int,
    ):
        result = self.db.execute(
            select(Lead).where(
                Lead.id == lead_id
            )
        )

        return result.scalar_one_or_none()

    # ======================================================
    # SAVE
    # ======================================================

    def save(
        self,
        lead: Lead,
    ):
        self.db.add(lead)

        self.db.flush()

        return lead

    def update(
            self,
            lead: Lead,
    ):
        self.db.flush()
