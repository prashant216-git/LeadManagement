from app.enums.channel import ConnectionStatus


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
            raise ValueError(
                "Channel watch not found."
            )

        return watch

    def resolve_access_token(
        self,
        connection_id: int,
    ) -> str:

        credential =  (
            self.credential_repository
            .get_by_connection_id(
                connection_id
            )
        )

        if credential is None:
            raise ValueError(
                "Channel credentials not found."
            )

        credentials = (
            self.credential_encryption_service
            .decrypt(
                credential.encrypted_payload
            )
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