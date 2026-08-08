import secrets
from secrets import token_urlsafe
from urllib.parse import urlencode

from app.channel_engine.BaseChannelProvider import BaseChannelProvider
from app.channel_engine.registry import ChannelProviderRegistry
from app.core.config import settings

from app.DTOs.connection.connection_request import ConnectRequest
from app.DTOs.connection.connection_response import ConnectResponse

from app.DTOs.messages_and_attachment.send_message_request import SendMessageRequest
from app.DTOs.messages_and_attachment.send_message_response import SendMessageResponse

# from app.schemas.channel.sync.sync_request import SyncRequest
# from app.schemas.channel.sync.sync_response import SyncResponse

from app.DTOs.health_check import (
    HealthCheckResponse,
)

from app.DTOs.messages_and_attachment.normalized_message import (
    NormalizedMessage,
)
from app.enums.channel import ConnectionStatus


@ChannelProviderRegistry.register("gmail")
class GmailProvider(BaseChannelProvider):

    def __init__(
        self,
        connection,
        credentials,
        connection_repository,
        credential_repository,
        encryption_service,
    ):
        self.connection = connection
        self.credentials = credentials

        self.connection_repository = connection_repository
        self.credential_repository = credential_repository
        self.encryption_service = encryption_service

    # ==========================================================
    # Connection Lifecycle
    # ==========================================================

    async def connect(
        self,
        request: ConnectRequest,
        state: str
    ) -> ConnectResponse:
        """
        Starts Google OAuth flow.

        This method only generates the authorization URL.

        No credentials are saved here.
        """

        if self.connection.connection_status == ConnectionStatus.CONNECTED:
            raise Exception("Channel already connected.")



        scopes = [
            "openid",
            "email",
            "profile",
            "https://www.googleapis.com/auth/gmail.modify",
        ]

        params = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "response_type": "code",
            "scope": " ".join(scopes),
            "access_type": "offline",
            "prompt": "consent",
            "state": state,
        }

        authorization_url = (
            "https://accounts.google.com/o/oauth2/v2/auth?"
            + urlencode(params)
        )

        return ConnectResponse(
            success=True,
            authorization_url=authorization_url,
            message="Redirect user to Google.",
        )

    async def oauth_callback(
        self,
        code: str,
        state: str,
    ):
        """
        Will be implemented later.

        Responsibilities:

        - Validate state
        - Exchange code
        - Fetch user profile
        - Encrypt credentials
        - Save credentials
        - Update connection
        """
        raise NotImplementedError()

    async def disconnect(self):
        raise NotImplementedError()

    async def refresh_credentials(self):
        raise NotImplementedError()

    async def health_check(
        self,
    ) -> HealthCheckResponse:
        raise NotImplementedError()

    # ==========================================================
    # Messaging
    # ==========================================================

    async def send_message(
        self,
        request: SendMessageRequest,
    ) -> SendMessageResponse:
        raise NotImplementedError()

    async def receive_message(self):
        raise NotImplementedError()

    # async def sync(
    #     self,
    #     request: SyncRequest,
    # ) -> SyncResponse:
    #     raise NotImplementedError()

    # ==========================================================
    # Webhooks
    # ==========================================================

    async def validate_webhook(self):
        raise NotImplementedError()

    async def normalize_webhook(
        self,
    ) -> NormalizedMessage:
        raise NotImplementedError()