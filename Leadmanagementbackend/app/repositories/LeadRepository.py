from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.Leads import Lead
from app.models.channel_connection import ChannelConnection
from sqlalchemy import select, func

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

    def get_leads_by_channel_id(
            self,
            channel_id: int,
            limit: int,
            offset: int,
            sort_by: str,
            sort_order: str,
    ):
        allowed_sort_fields = {
            "created_at": Lead.created_at,
            "name": Lead.name,
            "email": Lead.email,
        }

        sort_column = allowed_sort_fields.get(
            sort_by,
            Lead.created_at,
        )

        order_by = (
            sort_column.asc()
            if sort_order.lower() == "asc"
            else sort_column.desc()
        )

        query = (
            select(Lead)
            .join(
                ChannelConnection,
                Lead.channel_connection_id == ChannelConnection.id,
            )
            .where(
                ChannelConnection.channel_id == channel_id
            )
        )

        total = (
            self.db.execute(
                select(func.count(Lead.id))
                .join(
                    ChannelConnection,
                    Lead.channel_connection_id
                    == ChannelConnection.id,
                )
                .where(
                    ChannelConnection.channel_id
                    == channel_id
                )
            )
        ).scalar_one()

        result = self.db.execute(
            query
            .order_by(order_by)
            .offset(offset)
            .limit(limit)
        )

        return result.scalars().all(), total

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
