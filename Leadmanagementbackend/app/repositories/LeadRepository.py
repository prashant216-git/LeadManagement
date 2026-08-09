from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.Lead import Lead


class LeadRepository:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    # ======================================================
    # FIND LEAD
    # ======================================================

    async def get_by_identifier(
        self,
        tenant_id: int,
        identifier: str,
    ):
        """
        Find a lead belonging to a tenant.

        For the current implementation the identifier
        is matched against email or phone number.
        """

        result = await self.db.execute(
            select(Lead).where(
                Lead.tenant_id == tenant_id,
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

    async def get_by_id(
        self,
        lead_id: int,
    ):
        result = await self.db.execute(
            select(Lead).where(
                Lead.id == lead_id
            )
        )

        return result.scalar_one_or_none()

    # ======================================================
    # SAVE
    # ======================================================

    async def save(
        self,
        lead: Lead,
    ):
        self.db.add(lead)

        await self.db.flush()

        return lead