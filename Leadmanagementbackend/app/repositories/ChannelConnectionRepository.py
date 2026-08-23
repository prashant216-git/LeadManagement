from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.channel_connection import ChannelConnection
from app.enums.channel import ConnectionStatus


class ChannelConnectionRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    # ==========================================================
    # Get by ID
    # ==========================================================

    def get_by_id(
        self,
        connection_id: UUID,
    ) -> ChannelConnection | None:

        result = self.db.execute(
            select(ChannelConnection)
            .where(
                ChannelConnection.id == connection_id,

            )
        )

        return result.scalar_one_or_none()

    def get_by_oauth_state(
            self,

            oauth_state: str,
    ) -> ChannelConnection | None:
        result = self.db.execute(
            select(ChannelConnection)
            .where(

                ChannelConnection.oauth_state == oauth_state,
            )
        )

        return result.scalar_one_or_none()

    # ==========================================================
    # Get by Provider Account
    # ==========================================================

    def get_by_provider_identifier(
        self,
        channel_id: UUID,
        provider_account_identifier: str,
    ) -> ChannelConnection | None:

        result = self.db.execute(
            select(ChannelConnection)
            .where(
                ChannelConnection.channel_id == channel_id,
                ChannelConnection.provider_identifier
                == provider_account_identifier,ChannelConnection.connection_status== ConnectionStatus.CONNECTED,
            )
        )

        return result.scalar_one_or_none()

    # ==========================================================
    # Get Pending Connection
    # ==========================================================

    def get_pending_connection(
        self,
        user_id: UUID,
        channel_id: UUID,
        created_by: UUID,
    ) -> ChannelConnection | None:

        result = self.db.execute(
            select(ChannelConnection)
            .where(
                ChannelConnection.user_id == user_id,
                ChannelConnection.channel_id == channel_id,
                ChannelConnection.created_by == created_by,
                ChannelConnection.connection_status
                == ConnectionStatus.CONNECTING,
            )
        )

        return result.scalar_one_or_none()

    def get_connected_connection(
        self,
        user_id: UUID,
        channel_id: UUID,

    ) -> ChannelConnection | None:

        result = self.db.execute(
            select(ChannelConnection)
            .where(
                ChannelConnection.user_id == user_id,
                ChannelConnection.channel_id == channel_id,

                ChannelConnection.connection_status
                == ConnectionStatus.CONNECTED,
            )
        )



        return result.scalars().all()

    def get_all_by_tenant_and_channel(
            self,
            user_id: UUID,
            channel_id: UUID,
    ) -> list[ChannelConnection]:
        result =  self.db.execute(
            select(ChannelConnection)
            .where(
                ChannelConnection.user_id == user_id,
                ChannelConnection.channel_id == channel_id,
                ChannelConnection.connection_status== ConnectionStatus.CONNECTED,
            )
            .order_by(
                ChannelConnection.created_at.desc()
            )
        )

        return result.scalars().all()

    def save(
        self,
        connection: ChannelConnection,
    ) -> ChannelConnection:

        self.db.add(connection)

        self.db.commit()

        self.db.refresh(connection)

        return connection

    def update(
            self,
            connection: ChannelConnection,
    ) -> ChannelConnection:
        self.db.commit()

        self.db.refresh(connection)

        return connection