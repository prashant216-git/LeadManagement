from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.Leads import Lead
from app.models.channel_connection import ChannelConnection
from sqlalchemy import select, func

from app.models.channel_master import ChannelMaster


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
            user_id: UUID,
            source_channel_id: UUID | None=None,
            channel_connection_id: UUID | None = None,
            email: str | None = None,
            phone_number: str | None = None,
    ):
        conditions = [
            Lead.user_id == user_id,


        ]
        if source_channel_id:
            conditions.append(Lead.source_channel_id == source_channel_id)

        if email:
            conditions.append(
                Lead.email == email
            )

        elif phone_number:
            conditions.append(
                Lead.phone_number == phone_number
            )

        else:
            return None

        result = self.db.execute(
            select(Lead).where(*conditions)
        )

        return result.scalar_one_or_none()



    # ======================================================
    # GET BY ID
    # ======================================================

    def get_by_id(
        self,
        lead_id: UUID,
    ):
        result = self.db.execute(
            select(Lead).where(
                Lead.id == lead_id
            )
        )

        return result.scalar_one_or_none()

    def get_leads_by_channel_id(
            self,
            user_id: UUID,
            channel_id: UUID,
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
            select(
                Lead,
                ChannelConnection.provider_identifier,
            )
            .outerjoin(
                ChannelConnection,
                Lead.channel_connection_id
                == ChannelConnection.id,
            )
            .where(
                Lead.source_channel_id == channel_id,
                Lead.user_id == user_id,
            )
        )

        total = (
            self.db.execute(
                select(
                    func.count(Lead.id)
                )
                .where(
                    Lead.source_channel_id == channel_id,
                    Lead.user_id == user_id,
                )
            )
        ).scalar_one()

        result = self.db.execute(
            query
            .order_by(order_by)
            .offset(offset)
            .limit(limit)
        )

        return result.all(), total

    def get_manual_leads(
            self,
            user_id: UUID,
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
            .where(
                Lead.user_id == user_id,
                Lead.source_channel_id.is_(None),
            )
        )

        total = (
            self.db.execute(
                select(
                    func.count(Lead.id)
                )
                .where(
                    Lead.user_id == user_id,
                    Lead.source_channel_id.is_(None),
                )
            )
        ).scalar_one()

        result = self.db.execute(
            query
            .order_by(order_by)
            .offset(offset)
            .limit(limit)
        )

        return (
            result.scalars().all(),
            total,
        )

    # ======================================================
    # SAVE
    # ======================================================

    def save(
            self,
            lead: Lead,
    ) -> Lead:
        self.db.add(
            lead
        )

        self.db.commit()

        self.db.refresh(
            lead
        )

        return lead

    def update(
            self,
            lead: Lead,
    ):
        self.db.flush()
