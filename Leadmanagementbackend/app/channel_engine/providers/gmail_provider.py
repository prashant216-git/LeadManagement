import json
import re
import secrets
from email.mime.text import MIMEText
from email.utils import make_msgid
import base64
from datetime import datetime, timedelta, timezone
from os import access
from secrets import token_urlsafe
from urllib.parse import urlencode
import base64
from email.utils import make_msgid
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

        channelcodeid = (
            self.channel_resolver
            .resolve_channel_id(
                channel_code="gmail"
            )
        )

        print(channelcodeid)

        # 2. Resolve connection

        print(email_address)



        try:
            connectionid = (
                self.channel_resolver
                .resolve_connection_id(
                    channel_id=channelcodeid,
                    identifier=email_address,
                )
            )

        except ValueError as e:

            print(
                f"Ignoring Gmail notification: {e}"
            )

            return {
                "status": "ignored",
                "reason": "channel_disconnected_or_not_found",
            }

        if connectionid is None:
            return {
                "status": "ignored",
                "reason": "channel_disconnected Or Not Found",
            }

        # 3. Resolve watch
        print(connectionid)


        watch = (
            self.channel_resolver
            .resolve_watch(
                connection_id=connectionid
            )
        )

        if watch is None:
            return {
                "status": "ignored",
                "reason": "watch_not_found",
            }

        print(watch.provider_cursor)

        # ======================================================
        # IMPORTANT:
        # Don't hit Gmail if notification is already processed
        # ======================================================



        # 4. Access token

        accesstoken = (
            await self.channel_resolver
            .resolve_access_token(
                connection_id=connectionid
            )
        )

        if not accesstoken:
            return {
                "status": "ignored",
                "reason": "access_token_not_available",
            }

        print(accesstoken)

        # 5. Get new messages

        print("getting new messages")

        messages = await self._get_new_messages(
            watch.provider_cursor,
            accesstoken,
        )


        # 6. Create/update leads

        for message in messages:

            # IMPORTANT: check before extracting sender
            if message is None:
                print(
                    "Skipping unavailable Gmail message"
                )
                continue

            sender_details = self._extract_sender(
                message
            )

            if sender_details is None:
                continue

            sender = sender_details["sender"]
            recipient = sender_details["recipient"]

            lead_email = sender["email"]
            lead_name = sender["name"]

            if (
                    sender["email"].lower()
                    == email_address.lower()
            ):
                if recipient:
                    lead_email = recipient["email"]
                    lead_name = recipient["name"]

            createdlead = (
                await self.lead_service
                .create_or_update_lead(
                    source_channel_id=channelcodeid,
                    identifier=email_address,
                    email=lead_email,
                    name=lead_name,
                )
            )

            print(createdlead.id)

            message_details = (
                self._extract_message_data(
                    message
                )
            )

            reply_to_message_id = None
            direction = MessageDirection.INBOUND

            if message_details[
                "reply_to_message_id"
            ]:
                reply_to_message_id = (
                    await self.channel_resolver
                    .resolve_reply_to_message_id(
                        await self._resolve_rfc_message_id(
                            message_details[
                                "reply_to_message_id"
                            ],
                            access_token=accesstoken,
                        )
                    )
                )

            if (
                    sender["email"].lower()
                    == email_address.lower()
            ):
                direction = (
                    MessageDirection.OUTBOUND
                )

            await self.message_service.create_message(
                lead_id=createdlead.id,

                channel_connection_id=connectionid,

                conversation_id=(
                    message_details[
                        "conversation_id"
                    ]
                ),

                rfc_message_id=message_details.get(
                    "rfc_message_id"
                ),

                provider_message_id=(
                    message_details[
                        "provider_message_id"
                    ]
                ),

                reply_to_message_id=(
                    reply_to_message_id
                ),

                direction=direction,

                sender_identifier=(
                    sender["email"]
                ),

                recipient_identifier=(
                    recipient["email"]
                ),

                content=(
                    message_details["content"]
                ),

                message_type=(
                    message_details["message_type"]
                ),

                provider_created_at=(
                    message_details[
                        "provider_created_at"
                    ]
                ),
            )

        # 7. Update watch

        if int(history_id) > int(
                watch.provider_cursor
        ):
            watch.provider_cursor = (
                history_id
            )

            watch.last_event_at = (
                datetime.now(
                    timezone.utc
                )
            )

        self.channel_watch_repository.save(
            watch
        )

        return {
            "status": "processed",
            "email_address": email_address,
            "history_id": history_id,
        }

    async def send_message(
            self,
            connection,
            lead,
            content: str,
            reply_to_message_id: int | None = None,
    ):
        if not lead.email:
            raise ValueError(
                "Lead email is required."
            )

        access_token = (
            await self.channel_resolver
            .resolve_access_token(
                connection_id=connection.id
            )
        )

        # ==========================================
        # Generate RFC Message-ID
        # ==========================================

        rfc_message_id = make_msgid()

        email_message = MIMEText(
            content,
            "plain",
            "utf-8",
        )

        email_message["To"] = lead.email

        email_message["Message-ID"] = (
            rfc_message_id
        )

        thread_id = None

        # ==========================================
        # Reply
        # ==========================================

        if reply_to_message_id:

            parent_message = (
                self.channel_resolver
                .resolve_message_id(
                    message_id=reply_to_message_id
                )
            )

            if not parent_message:
                raise ValueError(
                    "Reply-to message not found."
                )

            if not parent_message.rfc_message_id:
                raise ValueError(
                    "Parent message does not have "
                    "an RFC Message-ID."
                )

            email_message["In-Reply-To"] = (
                parent_message.rfc_message_id
            )

            email_message["References"] = (
                parent_message.rfc_message_id
            )

            thread_id = (
                parent_message.conversation_id
            )

        # ==========================================
        # Encode MIME
        # ==========================================

        raw_message = (
            base64.urlsafe_b64encode(
                email_message.as_bytes()
            )
            .decode("utf-8")
        )

        # ==========================================
        # Send through Gmail
        # ==========================================

        sent_response = await self._send_message(
            raw_message=raw_message,
            access_token=access_token,
            thread_id=thread_id,
        )

        # ==========================================
        # Save outbound message
        # ==========================================

        await self.message_service.create_message(
            lead_id=lead.id,

            channel_connection_id=connection.id,

            conversation_id=(
                sent_response.get("threadId")
            ),

            provider_message_id=(
                sent_response.get("id")
            ),

            rfc_message_id=(
                rfc_message_id
            ),

            reply_to_message_id=(
                reply_to_message_id
            ),

            direction=MessageDirection.OUTBOUND,

            sender_identifier=(
                connection.provider_identifier
            ),

            recipient_identifier=(
                lead.email
            ),

            content=content,

            message_type=MessageType.TEXT,

            provider_created_at=datetime.now(timezone.utc),
        )

        return sent_response


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

        if response.status_code == 404:
            print(
                "Message not found in Gmail. "
                "Skipping message:",
                message_id,
            )

            return None



        response.raise_for_status()

        result = response.json()
        label_ids = result.get(
            "labelIds",
            [],
        )

        if "CATEGORY_PROMOTIONS" in label_ids:
            print(
                "Promotional message. Skipping:",
                message_id,
            )
            return None

        return result

    def _extract_sender(
            self,
            message: dict,
    ):
        headers = (
            message
            .get("payload", {})
            .get("headers", [])
        )

        sender_data = None
        recipient_data = None

        for header in headers:

            header_name = (
                header["name"].lower()
            )

            header_value = header["value"]

            # ==========================================
            # Sender
            # ==========================================

            if header_name == "from":

                match = re.match(
                    r"^(.*?)\s*<(.+?)>$",
                    header_value,
                )

                if match:
                    sender_data = {
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

                else:
                    sender_data = {
                        "name": None,
                        "email": header_value.strip(),
                    }

            # ==========================================
            # Recipient
            # ==========================================

            elif header_name == "to":

                match = re.match(
                    r"^(.*?)\s*<(.+?)>$",
                    header_value,
                )

                if match:
                    recipient_data = {
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

                else:
                    recipient_data = {
                        "name": None,
                        "email": header_value.strip(),
                    }

        if sender_data is None:
            return None

        return {
            "sender": sender_data,
            "recipient": recipient_data,
        }

    def _extract_body(
            self,
            message: dict,
    ):
        def decode_body(
                data: str | None,
        ) -> str | None:

            if not data:
                return None

            decoded = base64.urlsafe_b64decode(
                data + "=" * (-len(data) % 4)
            )

            return decoded.decode(
                "utf-8",
                errors="replace",
            )

        def clean_quoted_text(
                body: str,
        ) -> str:

            lines = body.splitlines()
            current_lines = []

            for index, line in enumerate(lines):

                stripped = line.strip().lower()

                # Gmail single-line reply separator
                #
                # On Sun, 23 Aug 2026 at 00:57,
                # Prashant <email@example.com> wrote:
                #
                if (
                        stripped.startswith("on ")
                        and stripped.endswith("wrote:")
                ):
                    break

                # Gmail multi-line reply separator
                #
                # On Sun, 23 Aug 2026 at 00:57,
                # Prashant <email@example.com>
                # wrote:
                #
                if (
                        stripped.startswith("on ")
                        and index + 1 < len(lines)
                        and lines[index + 1]
                        .strip()
                        .lower()
                        == "wrote:"
                ):
                    break

                # Standard quoted email line
                if line.lstrip().startswith(">"):
                    break

                current_lines.append(line)

            return "\n".join(
                current_lines
            ).strip()

        def find_body(
                part: dict,
        ) -> str | None:

            mime_type = part.get(
                "mimeType",
            )

            body_data = (
                part.get("body", {})
                .get("data")
            )

            # Prefer plain text body
            if (
                    mime_type == "text/plain"
                    and body_data
            ):
                return decode_body(
                    body_data,
                )

            # Search nested MIME parts
            for child in part.get(
                    "parts",
                    [],
            ):
                result = find_body(
                    child,
                )

                if result:
                    return result

            # Fallback to HTML body
            if (
                    mime_type == "text/html"
                    and body_data
            ):
                return decode_body(
                    body_data,
                )

            return None

        payload = message.get(
            "payload",
            {},
        )

        body = find_body(
            payload,
        )

        if not body:
            return None

        return clean_quoted_text(
            body,
        )

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

            print(header_map.get(
                "in-reply-to"))

        return {
            # Gmail conversation/thread
            "conversation_id": message.get(
                "threadId"
            ),

            # Gmail message ID
            "provider_message_id": message.get(
                "id"
            ),

            # RFC Message-ID of THIS email
            "rfc_message_id": header_map.get(
                "message-id"
            ),

            # RFC Message-ID of the email
            # this email is replying to
            "reply_to_message_id": header_map.get(
                "in-reply-to"
            ),

            # Message content
            "content": self._extract_body(
                message
            ),

            # Current implementation is text
            "message_type": MessageType.TEXT,

            # Gmail internal timestamp
            "provider_created_at": (
                provider_created_at
            ),
        }

    async def _resolve_rfc_message_id(
            self,
            rfc_message_id: str,
            access_token: str,
    ) -> str | None:

        if not rfc_message_id:
            return None

        print(
            "resolving RFC Message-ID:",
            rfc_message_id,
        )

        # Remove < > if Gmail header contains them
        rfc_message_id = rfc_message_id.strip()

        if (
                rfc_message_id.startswith("<")
                and rfc_message_id.endswith(">")
        ):
            rfc_message_id = rfc_message_id[1:-1]

        response = await self.client.get(
            "https://gmail.googleapis.com/gmail/v1/users/me/messages",
            headers={
                "Authorization": (
                    f"Bearer "
                    f"{access_token}"
                )
            },
            params={
                "q": f"rfc822msgid:{rfc_message_id}",
                "maxResults": 1,
            },
        )

        print(
            "resolve_rfc_message_id response:",
            response,
        )

        response.raise_for_status()

        data = response.json()

        messages = data.get("messages", [])

        if not messages:
            print(
                "No Gmail message found for RFC Message-ID:",
                rfc_message_id,
            )
            return None

        gmail_message_id = messages[0].get("id")

        print(
            "Resolved RFC Message-ID:",
            rfc_message_id,
            "-> Gmail message.id:",
            gmail_message_id,
        )

        return gmail_message_id

    async def _send_message(
            self,
            raw_message: str,
            access_token: str,
            thread_id: str | None = None,
    ):
        payload = {
            "raw": raw_message,
        }

        if thread_id:
            payload["threadId"] = thread_id

        response = await self.client.post(
            "https://gmail.googleapis.com/gmail/v1/users/me/messages/send",
            headers={
                "Authorization": (
                    f"Bearer {access_token}"
                ),
                "Content-Type": (
                    "application/json"
                ),
            },
            json=payload,
        )

        response.raise_for_status()

        return response.json()