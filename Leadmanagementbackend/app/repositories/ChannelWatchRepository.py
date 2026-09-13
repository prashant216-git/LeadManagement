from datetime import datetime
from uuid import UUID

from sqlalchemy import select

from app.models.ChannelWatch import ChannelWatch
from app.models.channel_connection import ChannelConnection


class ChannelWatchRepository:

    def __init__(self, db):
        self.db = db

    # ==========================================================
    # Get watch by connection ID
    # ==========================================================

    def get_by_connection_id(
        self,
        connection_id: UUID,
    ) -> ChannelWatch | None:

        result = self.db.execute(
            select(ChannelWatch).where(
                ChannelWatch.channel_connection_id == connection_id
            )
        )

        return result.scalar_one_or_none()

    def get_by_connection_id_for_update(
            self,
            connection_id: UUID,
    ) -> ChannelWatch | None:
        result = self.db.execute(
            select(ChannelWatch)
            .where(
                ChannelWatch.channel_connection_id
                == connection_id
            )
            .with_for_update()
        )

        return result.scalar_one_or_none()

    def get_watches_expiring_before(
            self,
            expiry_limit: datetime,
    ):
        statement = (
            select(
                ChannelWatch,
                ChannelConnection.id,
                ChannelConnection.provider_identifier,
                ChannelConnection.channel_id,
            )
            .join(
                ChannelConnection,
                ChannelConnection.id
                == ChannelWatch.channel_connection_id,
            )
            .where(
                ChannelWatch.expires_at <= expiry_limit,
                ChannelWatch.is_active.is_(True),
            )
        )

        result = self.db.execute(statement)

        return result.all()

    # ==========================================================
    # Save watch
    # ==========================================================

    def save(
        self,
        watch: ChannelWatch,
    ) -> ChannelWatch:

        self.db.add(watch)
        self.db.flush()

        return watch