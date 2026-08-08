from app.channel_engine.registry import ChannelProviderRegistry

from app.repositories.ChannelConnectionRepository import (
    ChannelConnectionRepository,
)

from app.repositories.ChannelCredentialRepository import (
    ChannelCredentialRepository,
)

from app.services.CredentialEncryptionService import (
    CredentialEncryptionService,
)


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
    ):
        self.connection_repository = connection_repository
        self.credential_repository = credential_repository
        self.credential_service = credential_service

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

        return provider_class(
            connection=connection,
            credentials=None,
            encryption_service=CredentialEncryptionService,
            credential_repository=ChannelCredentialRepository,
            connection_repository=ChannelConnectionRepository
        )

    # ==========================================================
    # EXISTING CONNECTION
    # ==========================================================

    async def get_provider(
        self,
        connection_id: int,
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

        connection = await (
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

        credential = await (
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