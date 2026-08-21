import secrets
from datetime import datetime, timezone

from app.DTOs import channelreponseDTO
from app.DTOs.connection.callbackerror import CallbackException
from app.DTOs.connection.connection_response import ConnectResponse
from app.channel_engine.engine import ChannelEngine
from datetime import datetime, timezone

from app.enums.channel import (
    ConnectionStatus,
    WatchStatus,
)
from app.DTOs.messages_and_attachment.send_message_request import (
    SendMessageRequest,
)
from app.channel_engine.channelresolver import ChannelResolver
from app.DTOs.channelreponseDTO import ConnectedAccountDTO
from app.models import tenant
from app.models.ChannelWatch import ChannelWatch
from app.channel_engine.registry import ChannelProviderRegistry
from app.enums.channel import ConnectionStatus
from app.enums.channel import CredentialType
from app.models.channel_credential import ChannelCredential
from app.models.channel_master import ChannelMaster
from app.repositories.ChannelCredentialRepository import ChannelCredentialRepository
from app.repositories.ChannelConnectionRepository import (
    ChannelConnectionRepository,
)
from app.repositories.ChannelWatchRepository import ChannelWatchRepository
from app.services.CredentialEncryptionService import CredentialEncryptionService

from app.repositories.ChannelMasterRepositories import (
    ChannelMasterRepository,
)

from app.DTOs.channelreponseDTO import ChannelResponseDTO


class ChannelService:

    def __init__(
        self,
        channel_engine: ChannelEngine,
        connection_repository: ChannelConnectionRepository,
        channel_master_repository: ChannelMasterRepository,
        credentials_repository : ChannelCredentialRepository,
        credential_encryption_service :CredentialEncryptionService,
        channel_watch_repository : ChannelWatchRepository,
        channel_resolver : ChannelResolver,


    ):
        self.channel_engine = channel_engine
        self.connection_repository = connection_repository
        self.channel_master_repository = channel_master_repository
        self.credentials_repository = credentials_repository
        self.credential_encryption_service = credential_encryption_service
        self.channel_watch_repository = channel_watch_repository
        self.channel_resolver = channel_resolver


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

        if (
                existing_connection is not None
                and existing_connection.connection_status
                == ConnectionStatus.CONNECTING):
            return ConnectResponse(
                success=True,
                authorization_url=existing_connection.connection_url,
                message="Redirect user to Google.")





        # ------------------------------------------------------
        # 3. Create pending connection
        # ------------------------------------------------------

        from app.models.channel_connection import (
            ChannelConnection,
        )
        random_state = secrets.token_urlsafe(15)[:20]
        tenantmasked = tenant_id + 1001
        state = f"{random_state}{tenantmasked}"
        connection = ChannelConnection(
            tenant_id=tenant_id,
            channel_id=channel.id,
            created_by=tenant_id,
            oauth_state=state
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


            result = await provider.connect(request=None,state=state)

            connection.connection_url = result.authorization_url

            self.connection_repository.update(connection)

            return result

        except Exception:

            connection.connection_status = ConnectionStatus.FAILED

            self.connection_repository.update(connection)

            raise

    async def handle_callback(
            self,
            channel_code: str,
            query_params: dict,
            headers: dict,
            body,
    ):
        state = None

        # ------------------------------------------------------
        # 1. Let engine resolve the provider
        # ------------------------------------------------------


        try:
            result = await self.channel_engine.handle_callback(
                channel_code=channel_code,
                query_params=query_params,
                headers=headers,
                body=body,
            )
        except CallbackException as e:
            state=e.error.state
            tenantmasked = int(state[20:])

            tenantid = tenantmasked - 1001

            connection = self.connection_repository.get_by_oauth_state(
                oauth_state=state, tenant_id=tenantid)
            if connection is not None:
                connection.connection_status = (
                    ConnectionStatus.FAILED
                )

                await self.connection_repository.save(
                    connection
                )

            raise HTTPException(
                status_code=400,
                detail=str(e),
            )










        state=result["state"]

        tenantmasked=int(state[20:])

        tenantid=tenantmasked-1001


        print(tenantid)

        # ------------------------------------------------------
        # 2. Get connection
        # ------------------------------------------------------

        connection = self.connection_repository.get_by_oauth_state(
            oauth_state=state,tenant_id=tenantid)

        if connection is None:
            raise ValueError(
                "No channel connection found for this OAuth state."
            )

        connection_id=connection.id



        if connection is None:
            raise ValueError(
                "Channel connection not found."
            )

        # ------------------------------------------------------
        # 3. Credentials returned by provider
        # ------------------------------------------------------

        credentials = result["credentials"]

        if credentials is None:
            raise ValueError(
                "Provider did not return credentials."
            )

        # ------------------------------------------------------
        # 4. Encrypt credentials
        # ------------------------------------------------------

        encrypted_payload = (
            self.credential_encryption_service.encrypt(credentials)

        )



        # ------------------------------------------------------
        # 5. Save credentials
        # ------------------------------------------------------
        credential = ChannelCredential(
            channel_connection_id=connection.id,
            credential_type=CredentialType.OAUTH,
            token_type=credentials["token_type"],
            expires_at=result["expires_at"],
            last_refreshed_at=datetime.now(timezone.utc),
            encrypted_payload=encrypted_payload,
            encryption_key_version=1,
            credential_version=1,
            is_active=True,
        )
        self.credentials_repository.save(
            credential
        )



        # ------------------------------------------------------
        # 6. Update connection
        # ------------------------------------------------------

        connection.connection_status = result["status"]

        connection.provider_account_id = (
            result.get("provider_account_id")
        )

        connection.provider_identifier = (
            result.get("provider_identifier")
        )

        connection.display_name = (
            result.get("display_name")
        )

        self.connection_repository.update(
            connection
        )

        # ------------------------------------------------------
        # 7. Don't expose credentials to API
        # ------------------------------------------------------

        return {
            "connection_id": connection.id,
            "status": connection.connection_status,
            "message": "Channel connected successfully.",
        }

    async def setup_watch(
            self,
            identifier:str,
            tenant_id: int,
            channel_code:str

    ):
        sourcename = self.channel_master_repository.get_by_code(
            channel_code=channel_code)


        connection = (
            self.connection_repository.get_by_provider_identifier(provider_account_identifier=identifier,channel_id=sourcename.id)
        )




        if connection is None:
            print(
                "No channel connection found for this OAuth state."
            )
            raise ValueError(
                "Gmail connection not found."
            )

        provider = self.channel_engine.create_provider(
            channel_code=sourcename.code,
            connection=connection,
        )

        print("her1")

        if provider is None:
            print(
                "No channel provider found for this OAuth state.")
            raise ValueError(
                "Gmail provider not found."
            )

        print("heree")



        return await provider.setup_watch(identifier=identifier,channel_id=sourcename.id)



    async def disconnect(
            self,
            connection_id: int,
    ):

        # ==================================================
        # 1. Resolve connection
        # ==================================================

        connection = (
            self.connection_repository
            .get_by_id(
                connection_id
            )
        )


        print(connection.id)

        if connection is None:
            raise ValueError(
                "Channel connection not found."
            )

        # ==================================================
        # 2. Already disconnected
        # ==================================================

        if (
                connection.connection_status
                == ConnectionStatus.DISCONNECTED
        ):
            return {
                "status": "already_disconnected",
                "connection_id": connection.id,
            }

        # ==================================================
        # 3. Resolve provider
        # ==================================================

        channel=self.channel_master_repository.get_by_id(connection.channel_id)
        if channel is None:
            raise ValueError("No channel found ")



        provider = self.channel_engine.create_provider(
            channel_code=channel.code,
            connection=connection,
        )

        print("yeaah")

        # ==================================================
        # 4. Disconnect provider
        # ==================================================

        await provider.disconnect(connection_id=connection_id)

        # ==================================================
        # 5. Update connection
        # ==================================================

        connection.connection_status = (
            ConnectionStatus.DISCONNECTED
        )

        connection.disconnected_at = datetime.now(
            timezone.utc
        )

        self.connection_repository.save(
            connection
        )

        # ==================================================
        # 6. Resolve watch
        # ==================================================

        watch = (
            self.channel_watch_repository
            .get_by_connection_id(
                connection_id
            )
        )

        # ==================================================
        # 7. Disable watch
        # ==================================================

        if watch is not None:
            watch.status = (
                WatchStatus.INACTIVE
            )

            watch.is_active = False

            self.channel_watch_repository.save(
                watch
            )

        return {
            "status": "disconnected",
            "connection_id": connection.id,
        }




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

    async def get_all_channels(
            self,
            tenant_id: int,
    ) -> list[ChannelResponseDTO]:



        channels =  (
            self.channel_master_repository
            .get_all()
        )

        result = []


        for channel in channels:

            connections =  (
                self.connection_repository
                .get_all_by_tenant_and_channel(
                    tenant_id=tenant_id,
                    channel_id=channel.id,
                )
            )

            connected_accounts = []

            for connection in connections:

                if (
                        connection.connection_status
                        == ConnectionStatus.CONNECTED
                ):
                    connected_accounts.append(
                        ConnectedAccountDTO(
                            id=connection.id,

                            provider_identifier=(
                                connection.provider_identifier
                            ),
                        )
                    )

            if connected_accounts:
                connection_status = "connected"
            else:
                connection_status = "pending"

            result.append(
                ChannelResponseDTO(
                    id=channel.id,
                    code=channel.code,
                    name=channel.name,
                    connection_status=connection_status,
                    connected_accounts=connected_accounts,
                )
            )

        return result




    async def handle_notification(
            self,
            channel_code: str,
            payload: dict,
    ):
        sourcename = self.channel_master_repository.get_by_code(
            channel_code=channel_code)





        provider = self.channel_engine.create_provider(
            channel_code=sourcename.code,
            connection=None,
        )



        if provider is None:
            print(
                "No channel provider found for this OAuth state.")
            raise ValueError(
                "Gmail provider not found."
            )




        return await provider.handle_notification(
            payload=payload,
        )

    async def resolve_connection_id(
            self,
            identifier: str,
            channel_id: int,
    ) -> int:

        connection = (
            self.connection_repository
            .get_by_provider_identifier(
                provider_account_identifier=identifier,
                channel_id=channel_id,
            )
        )

        if connection is None:
            raise ValueError(
                "Connected channel not found."
            )

        if (
                connection.connection_status
                != ConnectionStatus.CONNECTED
        ):
            raise ValueError(
                "Channel connection is not connected."
            )

        return connection.id

    async def resolve_watch(
            self,
            connection_id: int,
    ):

        watch = await (
            self.channel_watch_repository
            .get_by_connection_id(
                connection_id
            )
        )

        if watch is None:
            raise ValueError(
                "Channel watch not found."
            )

        return watch

    async def resolve_access_token(
            self,
            connection_id: int,
    ) -> str:

        credential = (
            self.credentials_repository
            .get_by_connection_id(
                connection_id
            )
        )

        if credential is None:
            raise ValueError(
                "Channel credentials not found."
            )



        return (self.credential_encryption_service.decrypt(
            credential.encrypted_payload
        ))["access_token"]