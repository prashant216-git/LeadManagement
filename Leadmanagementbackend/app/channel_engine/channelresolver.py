import httpx

from app.core.config import settings
from app.enums.channel import ConnectionStatus
from datetime import datetime, timezone, timedelta


class ChannelResolver:

    def __init__(
        self,
        connection_repository,
        credential_repository,
        channel_watch_repository,
        channel_master_repository,
        credential_encryption_service,
    ):
        self.connection_repository = connection_repository
        self.credential_repository = credential_repository
        self.channel_watch_repository = channel_watch_repository
        self.channel_master_repository = channel_master_repository
        self.credential_encryption_service = (
            credential_encryption_service
        )
        self.client = httpx.AsyncClient()

    def resolve_connection_id(
        self,
        identifier: str,
        channel_id: int,
    ) -> int:

        connection =  (
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

        return connection.id

    def resolve_watch(
        self,
        connection_id: int,
    ):

        watch =  (
            self.channel_watch_repository
            .get_by_connection_id(
                connection_id
            )
        )

        if watch is None:
            return None

        return watch

    async def resolve_access_token(
        self,
        connection_id: int,
    ) -> str:

        print("resolving token")

        credential =  (
            self.credential_repository
            .get_by_connection_id(
                connection_id
            )
        )

        credentials = (
            self.credential_encryption_service
            .decrypt(
                credential.encrypted_payload
            )
        )

        if credential is None:
            raise ValueError(
                "Channel credentials not found."
            )
        expires_at = credential.expires_at

        if expires_at is not None:


            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(
                    tzinfo=timezone.utc
                )

        refresh_token=credentials["refresh_token"]

        print(refresh_token)
        print("expires at",expires_at)
        print(datetime.now(timezone.utc) + timedelta(seconds=60))

        print(expires_at <= datetime.now(timezone.utc) + timedelta(seconds=60))


        if expires_at <= datetime.now(timezone.utc) + timedelta(seconds=60):
            return await self.refresh_access_token(
                connection_id=connection_id,
                refresh_token=refresh_token,
            )



        access_token = credentials["access_token"]

        if not access_token:
            raise ValueError(
                "Access token not found."
            )

        return access_token

    def resolve_channel_id(
            self,
            channel_code: str,
    ) -> int:

        channel = (
            self.channel_master_repository
            .get_by_code(
                channel_code=channel_code
            )
        )

        if channel is None:
            raise ValueError(
                f"Channel not found: {channel_code}"
            )

        return channel.id

    async def save_refreshed_credentials(
            self,
            connection_id: int,
            access_token: str,
            expires_in: int | None = None,
    ):

        credential = (
            self.credential_repository
            .get_by_connection_id(
                connection_id
            )
        )

        print("saving started")

        if credential is None:
            raise ValueError(
                "Channel credentials not found."
            )

        print("CREDENTIALS BEFORE ENCRYPT:", credential.encrypted_payload)

        credentials = (
            self.credential_encryption_service
            .decrypt(
                credential.encrypted_payload
            )
        )

        credentials["access_token"] = access_token

        if expires_in:
            expires_at = (
                    datetime.now(timezone.utc)
                    + timedelta(seconds=expires_in)
            ).isoformat()

        credential.expires_at = expires_at



        credential.encrypted_payload = (
            self.credential_encryption_service.encrypt(
                credentials
            )
        )


        credential.updated_at = datetime.now(
            timezone.utc
        )

        self.credential_repository.update(
            credential
        )

    async def refresh_access_token(
            self,
            connection_id: int,
            refresh_token: str,
    ) -> str:

        print("refreshing")

        # Ask Google for a new access token
        response = await self.client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "refresh_token": refresh_token,
                "grant_type": "refresh_token",
            },
        )

        response.raise_for_status()

        token_data = response.json()

        new_access_token = token_data.get("access_token")

        if not new_access_token:
            raise ValueError(
                "Google did not return a new access token."
            )

        expires_in = token_data.get("expires_in")

        if expires_in is None:
            raise ValueError(
                "Google did not return token expiry information."
            )



        # Save new credentials
        await self.save_refreshed_credentials(
            connection_id=connection_id,
            access_token=new_access_token,
            expires_in=expires_in,
        )

        print("access token refreshed")

        # Return token for immediate use
        return new_access_token



    async def resolve_refresh_token(
        self,
        connection_id: int,
    ) -> str:

        print("resolving token")

        credential =  (
            self.credential_repository
            .get_by_connection_id(
                connection_id
            )
        )

        credentials = (
            self.credential_encryption_service
            .decrypt(
                credential.encrypted_payload
            )
        )

        if credential is None:
            raise ValueError(
                "Channel credentials not found."
            )


        refresh_token=credentials["refresh_token"]



        return refresh_token