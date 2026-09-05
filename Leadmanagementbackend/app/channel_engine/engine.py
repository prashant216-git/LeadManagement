from uuid import UUID

from app.DTOs import connection

from app.channel_engine.registry import ChannelProviderRegistry

from app.repositories.ChannelConnectionRepository import (
    ChannelConnectionRepository,
)

from app.repositories.ChannelCredentialRepository import (
    ChannelCredentialRepository,
)
from app.repositories.ChannelMasterRepositories import ChannelMasterRepository
from app.repositories.ChannelWatchRepository import ChannelWatchRepository
from app.repositories.LeadRepository import LeadRepository

from app.services.CredentialEncryptionService import (
    CredentialEncryptionService,
)
from app.services.Leadmanagementservice import LeadService


class ChannelEngine:
    """
    Central engine for resolving and creating channel providers.

    Two important flows exist:

    1. New connection
       channel_code -> provider

    2. Existing connection
       connection_id -> connection
                     -> credentials
                     -> decrypt credentials
                     -> provider
    """

    def __init__(
        self,
        connection_repository: ChannelConnectionRepository,
        credential_repository: ChannelCredentialRepository,
        credential_service: CredentialEncryptionService,
        channel_watch_repository: ChannelWatchRepository,
        channel_master_repository:ChannelMasterRepository,
            lead_repository: LeadRepository,
            channel_resolver,
            message_service,
            db,
            webmanager,
    ):
        self.connection_repository = connection_repository
        self.credential_repository = credential_repository
        self.credential_service = credential_service
        self.channel_watch_repository = channel_watch_repository
        self.channel_master_repository = channel_master_repository
        self.lead_repository = lead_repository
        self.channel_resolver = channel_resolver
        self.message_service=message_service
        self.db=db
        self.web_socket_manager=webmanager

    # ==========================================================
    # NEW CONNECTION
    # ==========================================================

    def create_provider(
        self,
        channel_code: str,
        connection=None,


    ):
        """
        Create a provider for starting a new connection.

        At this stage credentials do NOT exist.

        Example:

            gmail
              ↓
            GmailProvider
              ↓
            connect()
              ↓
            Google OAuth
        """


        provider_class = (
            ChannelProviderRegistry.get(channel_code)
        )


        if provider_class is None:
            raise ValueError(
                f"Unsupported channel: {channel_code}"
            )
        print("ENGINE MANAGER:", id(self.web_socket_manager))

        return provider_class(
            connection=connection,
            credentials=None,
            encryption_service=self.credential_service,
            credential_repository=self.credential_repository,
            connection_repository=self.connection_repository,
            channel_watch_repository=self.channel_watch_repository,
            channel_master_repository=self.channel_master_repository,
            lead_service=LeadService(channel_connection_repository=self.connection_repository,
                                     lead_repository=self.lead_repository),
           channel_resolver=self.channel_resolver,
            message_service=self.message_service,db=self.db,
        websocketmanager=self.web_socket_manager


        )

    # ==========================================================
    # EXISTING CONNECTION
    # ==========================================================

    async def get_provider(
        self,
        connection_id: UUID,
    ):
        """
        Resolve a provider for an existing connection.

        Flow:

            connection_id
                ↓
            load connection
                ↓
            load credentials
                ↓
            decrypt credentials
                ↓
            resolve provider
                ↓
            create provider
        """

        # ------------------------------------------------------
        # 1. Load connection
        # ------------------------------------------------------

        connection = (
            self.connection_repository.get_by_id(
                connection_id
            )
        )

        if connection is None:
            raise ValueError(
                "Channel connection not found."
            )

        # ------------------------------------------------------
        # 2. Load credentials
        # ------------------------------------------------------

        credential = (
            self.credential_repository
            .get_by_connection_id(
                connection.id
            )
        )

        if credential is None:
            raise ValueError(
                "Channel credentials not found."
            )

        # ------------------------------------------------------
        # 3. Decrypt credentials
        # ------------------------------------------------------

        credentials = self.credential_service.decrypt(
            credential.encrypted_payload
        )

        # ------------------------------------------------------
        # 4. Resolve provider
        # ------------------------------------------------------

        provider_class = (
            ChannelProviderRegistry.get(
                connection.channel.code
            )
        )

        if provider_class is None:
            raise ValueError(
                f"Unsupported channel: "
                f"{connection.channel.code}"
            )

        # ------------------------------------------------------
        # 5. Build provider
        # ------------------------------------------------------

        return provider_class(
            connection=connection,
            credentials=credentials,
        )

    async def handle_callback(
            self,
            channel_code: str,
            query_params: dict,
            headers: dict,
            body,
    ):

        provider_class = (
            ChannelProviderRegistry.get(
                channel_code
            )
        )

        provider_class=provider_class(
            connection=connection,
            credentials=None,
            encryption_service=CredentialEncryptionService,
            credential_repository=ChannelCredentialRepository,
            connection_repository=ChannelConnectionRepository,
            channel_watch_repository=self.channel_watch_repository,
            channel_master_repository=self.channel_master_repository,
            channel_resolver=self.channel_resolver,
            message_service=self.message_service,
            lead_service=LeadService(channel_connection_repository=self.connection_repository,lead_repository=self.lead_repository),
            db=self.db,
            websocketmanager=self.web_socket_manager

        )

        return await provider_class.handle_callback(
            query_params=query_params,
            headers=headers,
            body=body,
        )