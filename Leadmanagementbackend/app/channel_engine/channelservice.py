import secrets

from app.channel_engine.engine import ChannelEngine

from app.DTOs.messages_and_attachment.send_message_request import (
    SendMessageRequest,
)
from app.channel_engine.registry import ChannelProviderRegistry
from app.enums.channel import ConnectionStatus

from app.repositories.ChannelConnectionRepository import (
    ChannelConnectionRepository,
)

from app.repositories.ChannelMasterRepositories import (
    ChannelMasterRepository,
)


class ChannelService:

    def __init__(
        self,
        channel_engine: ChannelEngine,
        connection_repository: ChannelConnectionRepository,
        channel_master_repository: ChannelMasterRepository,
    ):
        self.channel_engine = channel_engine
        self.connection_repository = connection_repository
        self.channel_master_repository = channel_master_repository

    # ==========================================================
    # NEW CONNECTION
    # ==========================================================

    async def connect(
        self,
        tenant_id: int,
        channel_code: str,
    ):
        """
        Start a new channel connection.

        Flow:

            JWT
             ↓
            tenant_id + user_id
             ↓
            channel_code
             ↓
            ChannelMaster
             ↓
            Create ChannelConnection
             ↓
            ChannelEngine
             ↓
            Provider
             ↓
            OAuth
        """

        # ------------------------------------------------------
        # 1. Resolve channel master
        # ------------------------------------------------------

        channel = (
            self.channel_master_repository
            .get_by_code(channel_code)
        )

        if channel is None:
            raise ValueError(
                f"Unsupported channel: {channel_code}"
            )

        # ------------------------------------------------------
        # 2. Check for an existing pending connection
        # ------------------------------------------------------

        existing_connection = (
            self.connection_repository
            .get_pending_connection(
                tenant_id=tenant_id,
                channel_id=channel.id,
                created_by=tenant_id,
            )
        )

        if existing_connection is not None:
            raise ValueError(
                "A connection is already being established."
            )

        # ------------------------------------------------------
        # 3. Create pending connection
        # ------------------------------------------------------

        from app.models.channel_connection import (
            ChannelConnection,
        )
        random_state = secrets.token_urlsafe(15)[:20]
        tenant_id = tenant_id + 1001
        state = f"{random_state}{tenant_id}"
        connection = ChannelConnection(
            tenant_id=tenant_id,
            channel_id=channel.id,
            created_by=tenant_id,
            
        )
        connection = self.connection_repository.save(
            connection
        )



        # ------------------------------------------------------
        # 4. Create provider for NEW connection
        # ------------------------------------------------------

        try:
            print(ChannelProviderRegistry._providers)

            provider = self.channel_engine.create_provider(
                channel_code=channel_code,
                connection=connection,
            )


            result = await provider.connect(request=None,tenant_id=tenant_id)

            connection.connection_url = result.authorization_url

            self.connection_repository.update(connection)

            return result

        except Exception:

            connection.connection_status = ConnectionStatus.FAILED

            self.connection_repository.update(connection)

            raise
        # ------------------------------------------------------
        # 5. Start provider connection
        # ------------------------------------------------------

        return provider.connect()

    # ==========================================================
    # EXISTING CONNECTION
    # ==========================================================

    async def disconnect(
        self,
        connection_id: int,
    ):
        """
        Disconnect an existing channel connection.
        """

        provider = self.channel_engine.get_provider(
            connection_id
        )

        return provider.disconnect()

    # ==========================================================
    # SEND MESSAGE
    # ==========================================================

    async def send_message(
        self,
        connection_id: int,
        request: SendMessageRequest,
    ):
        """
        Send a message using an existing connection.
        """

        provider = self.channel_engine.get_provider(
            connection_id
        )

        return provider.send_message(
            request
        )