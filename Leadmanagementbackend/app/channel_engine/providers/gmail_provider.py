import json
import secrets
from datetime import datetime, timedelta, timezone
from secrets import token_urlsafe
from urllib.parse import urlencode
import base64
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
from app.enums.channel import ConnectionStatus, WatchStatus

import httpx

from app.models.ChannelWatch import ChannelWatch


@ChannelProviderRegistry.register("gmail")
class GmailProvider(BaseChannelProvider):

    def __init__(
        self,
        connection,
        credentials,
        connection_repository,
        credential_repository,
        encryption_service,
        channel_watch_repository,
        channel_master_repository
    ):
        self.connection = connection
        self.credentials = credentials

        self.connection_repository = connection_repository
        self.credential_repository = credential_repository
        self.encryption_service = encryption_service
        self.channel_watch_repository = channel_watch_repository
        self.client = httpx.AsyncClient()
        self.channel_master_repository=channel_master_repository

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

    async def handle_callback(
            self,
            query_params: dict,
            headers: dict,
            body,
    ):
        # ------------------------------------------------------
        # 1. Extract OAuth parameters
        # ------------------------------------------------------

        code = query_params.get("code")
        state = query_params.get("state")
        error = query_params.get("error")

        if error:
            raise ValueError(
                f"Google OAuth failed: {error}"
            )

        if not code:
            raise ValueError(
                "Google authorization code is missing."
            )

        if not state:
            raise ValueError(
                "Google OAuth state is missing."
            )

        # ------------------------------------------------------
        # 2. Exchange code for tokens
        # ------------------------------------------------------

        token_data = await self._exchange_code(code)

        access_token = token_data.get("access_token")
        refresh_token = token_data.get("refresh_token")

        if not access_token:
            raise ValueError(
                "Google did not return an access token."
            )

        # ------------------------------------------------------
        # 3. Extract token information
        # ------------------------------------------------------

        expires_in = token_data.get("expires_in")

        expires_at = None

        if expires_in:
            expires_at = (
                    datetime.now(timezone.utc)
                    + timedelta(seconds=expires_in)
            ).isoformat()

        # ------------------------------------------------------
        # 4. Get Google account information
        # ------------------------------------------------------

        account = await self._get_account(
            access_token
        )

        # ------------------------------------------------------
        # 5. Extract provider identity
        # ------------------------------------------------------

        provider_account_id = account.get("sub")
        email = account.get("email")
        display_name = account.get("name")

        if not provider_account_id:
            raise ValueError(
                "Google account ID was not returned."
            )

        if not email:
            raise ValueError(
                "Google account email was not returned."
            )

        # ------------------------------------------------------
        # 6. Return normalized provider result
        # ------------------------------------------------------

        return {
            "state": state,

            "status": ConnectionStatus.CONNECTED,

            "provider_account_id": provider_account_id,

            "provider_identifier": email,

            "display_name": display_name or email,
            "expires_at": expires_at,

            "credentials": {
                "access_token": access_token,

                "refresh_token": refresh_token,

                "token_type": token_data.get(
                    "token_type"
                ),



                "scope": token_data.get(
                    "scope"
                ),
            },
        }


    async def _exchange_code(
        self,
        code: str,
    ):

        client_id = settings.GOOGLE_CLIENT_ID


        client_secret = settings.GOOGLE_CLIENT_SECRET
        redirect_uri = settings.GOOGLE_REDIRECT_URI

        if not client_id:
            raise ValueError(
                "GOOGLE_CLIENT_ID is not configured."
            )

        if not client_secret:
            raise ValueError(
                "GOOGLE_CLIENT_SECRET is not configured."
            )

        if not redirect_uri:
            raise ValueError(
                "GOOGLE_REDIRECT_URI is not configured."
            )

        data = {
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        }

        async with httpx.AsyncClient() as client:

            response = await client.post(
                "https://oauth2.googleapis.com/token",
                data=data,
            )

        if response.status_code != 200:

            raise ValueError(
                f"Google token exchange failed: "
                f"{response.text}"
            )

        return response.json()

    # ==========================================================
    # ACCOUNT INFORMATION
    # ==========================================================

    async def _get_account(
        self,
        access_token: str,
    ):

        headers = {
            "Authorization": (
                f"Bearer {access_token}"
            )
        }

        async with httpx.AsyncClient() as client:

            response = await client.get(
                "https://openidconnect.googleapis.com/v1/userinfo",
                headers=headers,
            )

        if response.status_code != 200:

            raise ValueError(
                f"Unable to retrieve Google account: "
                f"{response.text}"
            )

        return response.json()

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

    async def setup_watch(self,access_token:str):

        response = await self.client.post(
            "https://gmail.googleapis.com/gmail/v1/users/me/watch",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            },
            json={
                "labelIds": ["INBOX"],
                "topicName": "projects/project-b00ec870-b58a-41a5-8a4/topics/gmail-events",
            },
        )

        response.raise_for_status()

        data = response.json()

        watch = self.channel_watch_repository.get_by_connection_id(
            self.connection.id
        )

        now = datetime.now(timezone.utc)

        if watch is None:
            watch = ChannelWatch(
                channel_connection_id=self.connection.id,
                provider_subscription_id=None,
                provider_resource_id=None,
                provider_cursor=data["historyId"],
                status=WatchStatus.ACTIVE,
                started_at=now,
                expires_at=datetime.fromtimestamp(
                    int(data["expiration"]) / 1000,
                    tz=timezone.utc,
                ),
                last_renewed_at=now,
                provider_metadata={
                    "provider": "gmail"
                },
                is_active=True,
            )

            self.channel_watch_repository.save(watch)

        else:
            watch.provider_cursor = response["historyId"]
            watch.expires_at = datetime.fromtimestamp(
                int(response["expiration"]) / 1000,
                tz=timezone.utc,
            )
            watch.last_renewed_at = now
            watch.status = WatchStatus.ACTIVE
            watch.is_active = True

            self.channel_watch_repository.save(watch)

        return {
            "status": "WATCH_ACTIVE",
            "connection_id": self.connection.id,
        }

    async def handle_notification(
            self,
            payload: dict,
    ):
        """
        Handles a Gmail Pub/Sub notification.

        Gmail-specific responsibilities:
        - Decode Pub/Sub payload
        - Resolve Gmail notification
        - Get/update ChannelWatch
        - Fetch Gmail history
        - Fetch new messages
        - Save messages
        - Trigger lead processing afterwards
        """

        # ==================================================
        # 1. Resolve Gmail notification
        # ==================================================

        decoded = base64.b64decode(payload["message"]["data"]).decode("utf-8")
        notifications = json.loads(decoded)



        email_address = notifications["emailAddress"]
        history_id = str(notifications["historyId"])

        channels=self.channel_master_repository.get_by_code(channel_code="gmail")

        connection = self.connection_repository.get_by_provider_identifier(provider_account_identifier=email_address,channel_id=channels.id)

        # ==================================================
        # 2. Resolve / update watch
        # ==================================================

        watch = (
            self.channel_watch_repository
            .get_by_connection_id(
                connection.id
            )
        )

        if watch is None:
            raise ValueError(
                "Gmail watch not found."
            )

        previous_history_id = (
            watch.provider_cursor
        )

        print("GMAIL NOTIFICATION:", notifications)
        print("CONNECTION ID:", connection.id)
        print("HISTORY ID:", history_id)

        # ==================================================
        # 3. Get Gmail history
        # ==================================================

        # history = await self._get_history(
        #     start_history_id=previous_history_id,
        # )

        # ==================================================
        # 4. Process new messages
        # ==================================================

        # messages = []
        #
        # for history_record in history:
        #
        #     history_messages = (
        #         history_record.get(
        #             "messagesAdded",
        #             []
        #         )
        #     )

            # for item in history_messages:
            #     message = await self._get_message(
            #         item["message"]["id"]
            #     )
            #
            #     messages.append(message)

        # ==================================================
        # 5. Update watch cursor
        # ==================================================

        watch.provider_cursor = history_id
        watch.last_event_at = datetime.now(
            timezone.utc
        )

        self.channel_watch_repository.save(
            watch
        )

        # ==================================================
        # 6. Save messages
        # ==================================================

        # for message in messages:
        #     await self._save_message(
        #         message
        #     )
        #
        # # ==================================================
        # # 7. Lead processing
        # # ==================================================
        #
        # for message in messages:
        #     await self._process_lead(
        #         message
        #     )

        return {
            "status": "processed",
            "email_address": email_address,
            "history_id": history_id,

        }