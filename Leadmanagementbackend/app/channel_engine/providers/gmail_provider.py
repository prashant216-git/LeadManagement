import json
import re
import secrets
from datetime import datetime, timedelta, timezone
from os import access
from secrets import token_urlsafe
from urllib.parse import urlencode
import base64

from app.DTOs.connection.callbackerror import CallbackError, CallbackException
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

from app.enums.message import MessageDirection, MessageType
from app.models import channel_connection
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
        channel_master_repository,
        lead_service,

        channel_resolver,
        message_service

    ):
        self.connection = connection
        self.credentials = credentials

        self.connection_repository = connection_repository
        self.credential_repository = credential_repository
        self.encryption_service = encryption_service
        self.channel_watch_repository = channel_watch_repository
        self.client = httpx.AsyncClient()
        self.channel_master_repository=channel_master_repository
        self.lead_service = lead_service
        self.message_service = message_service

        self.channel_resolver=channel_resolver

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
            raise CallbackException( CallbackError(message=error,state=state))


        if not code:
            CallbackException(
                CallbackError(
                    message="Google authorization code is missing.",
                    state=state
                ))

        if not state:
            raise CallbackException(
                CallbackError(
                    message="Google OAuth state is missing.",
                    state=state
                ))

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

    async def disconnect(
            self,
            connection_id: int
    ):
        """
        Disconnect Gmail provider.

        1. Stop the active Gmail watch.
        2. Revoke the Google OAuth credentials.
        """

        access_token = await self.channel_resolver.resolve_access_token(
            connection_id
        )

        if not access_token:
            raise ValueError("Gmail access token not found.")

        refresh_token = await self.channel_resolver.resolve_refresh_token(
            connection_id
        )

        if not refresh_token:
            raise ValueError("Gmail refresh token not found.")

        # --------------------------------------------------
        # 1. Stop Gmail Watch
        # --------------------------------------------------


        watch = self.channel_resolver.resolve_watch(
            connection_id
        )
        print("yeah")

        if watch is not None:
            response = await self.client.post(
                "https://gmail.googleapis.com/gmail/v1/users/me/stop",
                headers={
                    "Authorization": f"Bearer {access_token}",
                },
            )

            response.raise_for_status()

        # --------------------------------------------------
        # 2. Revoke Google OAuth credentials
        # --------------------------------------------------

        response = await self.client.post(
            "https://oauth2.googleapis.com/revoke",
            data={
                "token": refresh_token,
            },
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
            },
        )

        response.raise_for_status()

        return {
            "status": "provider_disconnected",
        }

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

    async def setup_watch(self,identifier:str,channel_id:int):

        connectionid=self.channel_resolver.resolve_connection_id(identifier=identifier,channel_id=channel_id)

        access_token=await self.channel_resolver.resolve_access_token(connection_id=connectionid)

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
        # 1. Decode notification
        decoded = base64.b64decode(
            payload["message"]["data"]
        ).decode("utf-8")

        notification = json.loads(decoded)

        email_address = notification["emailAddress"]
        history_id = str(notification["historyId"])

        channelcodeid= self.channel_resolver.resolve_channel_id(channel_code="gmail")

        print(channelcodeid)

        # 2. Resolve connection

        print(email_address)

        connectionid =   self.channel_resolver.resolve_connection_id(channel_id=channelcodeid,identifier=email_address)
        print(connectionid)

        if connectionid is None:
            return {
                "status": "ignored",
                "reason": "channel_disconnected Or Not Found",
            }
        watch =   self.channel_resolver.resolve_watch(connection_id=connectionid)

        print(watch.provider_cursor)

        accesstoken = await self.channel_resolver.resolve_access_token(connection_id=connectionid)

        print(accesstoken)



        # 4. Get new messages

        print("getting new messages")
        messages = await self._get_new_messages(
            watch.provider_cursor,
            accesstoken
        )

        # 5. Create/update leads
        for message in messages:

            sender = self._extract_sender(
                message
            )

            if sender is None:
                continue

            createdlead=await self.lead_service.create_or_update_lead(
                channel_id=channelcodeid,
                identifier=email_address,
                email=sender["email"],
                name=sender["name"]
            )

            print(createdlead.id)
            await self.message_service.create_message(
                lead_id=createdlead.id,
                channel_connection_id=connectionid,
                provider_message_id=message["id"],
                direction=MessageDirection.INBOUND,
                sender_identifier=sender["email"],
                recipient_identifier=email_address,
                content=self._extract_body(message),
                message_type=MessageType.TEXT,
                provider_created_at=datetime.fromtimestamp(
                    int(message["internalDate"]) / 1000,
                    tz=timezone.utc,
                ),
                provider_metadata={
                    "thread_id": message.get("threadId"),
                },
            )




        # 6. Update watch

        if int(history_id) > int(watch.provider_cursor):
            watch.provider_cursor = history_id

            watch.last_event_at = datetime.now(
                timezone.utc
            )

        self.channel_watch_repository.save(
            watch
        )

        return {
            "status": "processed",
            "email_address": email_address,
            "history_id": history_id,
        }

    async def _get_new_messages(
            self,
            history_id: str,
            access_token: str,
    ):
        print(access_token)
        response = await self.client.get(
            "https://gmail.googleapis.com/gmail/v1/users/me/history",
            headers={
                "Authorization": (
                    f"Bearer "
                    f"{access_token}"
                )
            },
            params={
                "startHistoryId": history_id,
                "historyTypes": "messageAdded",
            },
        )
        print("newmessage extraction done")
        print("getnewmessage",response)

        response.raise_for_status()

        history = response.json()

        messages = []

        for record in history.get("history", []):

            for item in record.get(
                    "messagesAdded",
                    []
            ):
                message_id = item["message"]["id"]

                message = await self._get_message(
                    message_id=message_id,
                    access_token=access_token,
                )

                messages.append(message)

        return messages

    async def _get_message(
            self,
            message_id: str,
            access_token: str,
    ):

        print("getting single messages")
        response = await self.client.get(
            f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{message_id}",
            headers={
                "Authorization": (
                    f"Bearer "
                    f"{access_token}"
                )
            },
            params={
                 "format": "full",

            },
        )

        print("get_message",response)

        response.raise_for_status()

        return response.json()

    def _extract_sender(
            self,
            message: dict,
    ):
        headers = (
            message
            .get("payload", {})
            .get("headers", [])
        )

        for header in headers:

            if header["name"].lower() != "from":
                continue

            sender = header["value"]

            match = re.match(
                r"^(.*?)\s*<(.+?)>$",
                sender,
            )

            if match:
                return {
                    "name": (
                        match.group(1)
                        .strip()
                        .strip('"')
                    ),
                    "email": (
                        match.group(2)
                        .strip()
                    ),
                }

            return {
                "name": None,
                "email": sender.strip(),
            }

        return None

    def _extract_body(
            self,
            message: dict,
    ):
        def decode_body(data: str | None):
            if not data:
                return None

            decoded = base64.urlsafe_b64decode(
                data + "=" * (-len(data) % 4)
            )

            return decoded.decode(
                "utf-8",
                errors="replace",
            )

        def find_body(part: dict):
            mime_type = part.get("mimeType")
            body_data = (
                part.get("body", {})
                .get("data")
            )

            # Prefer plain text
            if mime_type == "text/plain" and body_data:
                return decode_body(body_data)

            # Search nested MIME parts
            for child in part.get("parts", []):
                result = find_body(child)

                if result:
                    return result

            # Fallback to HTML
            if mime_type == "text/html" and body_data:
                return decode_body(body_data)

            return None

        payload = message.get("payload", {})

        return find_body(payload)

    def _extract_message_data(
            self,
            message: dict,
    ) -> dict:
        headers = message.get(
            "payload",
            {},
        ).get(
            "headers",
            [],
        )

        header_map = {
            header.get("name", "").lower(): header.get("value")
            for header in headers
        }
        provider_created_at = None

        if message.get("internalDate"):
            provider_created_at = datetime.fromtimestamp(
                int(message["internalDate"]) / 1000
            )

        return {
            # Gmail conversation/thread
            "conversation_id": message.get("threadId"),

            # Gmail message ID
            "provider_message_id": message.get("id"),

            # Gmail Message-ID of the message being replied to
            "reply_to_message_id": header_map.get(
                "in-reply-to"
            ),

            # Sender
            "sender_identifier": self._extract_email(
                header_map.get("from")
            ),

            # Recipient
            "recipient_identifier": self._extract_email(
                header_map.get("to")
            ),

            # Message content
            "content": self._extract_body(
                message
            ),

            # Current implementation is text
            "message_type": MessageType.TEXT,

            # Gmail internal timestamp
            "provider_created_at": provider_created_at
            ),
        }