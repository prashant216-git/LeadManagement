from uuid import UUID

from sqlalchemy import select

from app.models.ChannelWatch import ChannelWatch


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

    # ==========================================================
    # Save watch
    # ==========================================================

    def save(
        self,
        watch: ChannelWatch,
    ) -> ChannelWatch:

        self.db.add(watch)
        self.db.commit()
        self.db.refresh(watch)

        return watch