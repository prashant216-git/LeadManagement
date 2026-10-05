from urllib.parse import urlencode

import httpx
from fastapi import HTTPException
from starlette.responses import PlainTextResponse

from app.DTOs.connection.callbackerror import CallbackException, CallbackError
from app.DTOs.connection.connection_request import ConnectRequest
from app.DTOs.connection.connection_response import ConnectResponse
from app.channel_engine.BaseChannelProvider import BaseChannelProvider
from app.channel_engine.registry import ChannelProviderRegistry
from app.core.config import settings
from app.enums.channel import ConnectionStatus


@ChannelProviderRegistry.register("meta")
class MetaProvider(BaseChannelProvider):

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
        message_service,
            db,
            websocketmanager

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
        self.db=db
        self.META_GRAPH_URL = (
            f"https://graph.facebook.com/"
            f"{settings.META_GRAPH_API_VERSION}"
        )

    async def verify_webhook(
            self,
            query_params: dict,
    ):
        # =========================================================
        # Meta Webhook Verification
        # =========================================================

        print("insiude meta servie")

        hub_mode = query_params.get(
            "hub.mode"
        )

        hub_verify_token = query_params.get(
            "hub.verify_token"
        )

        hub_challenge = query_params.get(
            "hub.challenge"
        )

        # ---------------------------------------------------------
        # Validate Meta verification request
        # ---------------------------------------------------------

        if hub_mode != "subscribe":
            raise HTTPException(
                status_code=403,
                detail="Invalid webhook mode.",
            )

        if hub_verify_token != settings.VERIFY_TOKEN:
            raise HTTPException(
                status_code=403,
                detail="Invalid webhook verification token.",
            )

        if not hub_challenge:
            raise HTTPException(
                status_code=400,
                detail="Webhook challenge is missing.",
            )

        # ---------------------------------------------------------
        # Meta expects the challenge as plain text
        # ---------------------------------------------------------

        return PlainTextResponse(
            content=hub_challenge
        )

    async def connect(
            self,
            request: ConnectRequest,
            state: str,
    ) -> ConnectResponse:
        if (
                self.connection.connection_status
                == ConnectionStatus.CONNECTED
        ):
            raise ValueError(
                "META channel already connected."
            )

        return ConnectResponse(
            success=True,
            config_id=settings.META_EMBEDDED_SIGNUP_CONFIG_ID,
            message="Start Meta Embedded Signup.",
            state=state,
        )

    async def handle_callback(
            self,
            query_params: dict,
            headers: dict,
            body: dict,
    ):
        """
        Handle generic Meta Embedded Signup callback.

        One Meta authorization can result in multiple
        channel connections such as WhatsApp and Instagram.
        """

        # =========================================================
        # 1. Validate body
        # =========================================================

        if not body:
            raise CallbackException(
                CallbackError(
                    message="Meta callback body is missing.",
                    state=None,
                )
            )

        # =========================================================
        # 2. Extract state
        # =========================================================

        state = body.get("state")

        if not state:
            raise CallbackException(
                CallbackError(
                    message="Meta OAuth state is missing.",
                    state=None,
                )
            )

        # =========================================================
        # 3. Extract Meta payload
        # =========================================================

        payload = body.get("payload")

        if not payload:
            raise CallbackException(
                CallbackError(
                    message="Meta callback payload is missing.",
                    state=state,
                )
            )

        # =========================================================
        # 4. Handle Meta error
        # =========================================================

        error = payload.get("error")

        if error:
            raise CallbackException(
                CallbackError(
                    message=str(error),
                    state=state,
                )
            )

        # =========================================================
        # 5. Extract access token
        # =========================================================

        access_token = payload.get("access_token")

        if not access_token:
            raise CallbackException(
                CallbackError(
                    message="Meta access token is missing.",
                    state=state,
                )
            )

        # =========================================================
        # 6. Extract optional WhatsApp information
        # =========================================================

        waba_id = payload.get("waba_id")
        phone_number_id = payload.get("phone_number_id")

        channels = []

        # =========================================================
        # 7. WhatsApp
        # =========================================================

        if waba_id and phone_number_id:
            phone_number = await self._get_phone_number(
                phone_number_id=phone_number_id,
                access_token=access_token,
            )

            display_phone_number = (
                phone_number.get("display_phone_number")
            )

            verified_name = (
                phone_number.get("verified_name")
            )

            channels.append(
                {
                    "channel_code": "meta",
                    "channel_name": "WhatsApp",

                    "status": ConnectionStatus.CONNECTED,

                    "provider_account_id": waba_id,

                    "provider_identifier": phone_number_id,

                    "display_name": (
                            verified_name
                            or display_phone_number
                            or "WhatsApp"
                    ),

                    "provider_metadata": {
                        "waba_id": waba_id,
                        "phone_number_id": phone_number_id,
                        "display_phone_number": display_phone_number,
                        "verified_name": verified_name,
                    },
                }
            )

        # =========================================================
        # 8. Instagram
        # =========================================================

        instagram_accounts = await self._get_instagram_accounts(
            access_token=access_token,
        )

        for instagram in instagram_accounts:
            channels.append(
                {
                    "channel_code": "meta",
                    "channel_name": "Instagram",

                    "status": ConnectionStatus.CONNECTED,

                    "provider_account_id": instagram["id"],

                    "provider_identifier": instagram.get(
                        "username"
                    ),

                    "display_name": (
                            instagram.get("username")
                            or instagram.get("name")
                            or "Instagram"
                    ),

                    "provider_metadata": instagram,
                }
            )

        # =========================================================
        # 9. Nothing discovered
        # =========================================================

        if not channels:
            raise CallbackException(
                CallbackError(
                    message=(
                        "Meta authorization succeeded, "
                        "but no supported WhatsApp or Instagram "
                        "account was found."
                    ),
                    state=state,
                )
            )

        # =========================================================
        # 10. Shared credentials
        # =========================================================

        return {
            "state": state,

            "credentials": {
                "access_token": access_token,
                "refresh_token": None,
                "token_type": "Bearer",
            },

            "channels": channels,
        }

    async def _get_instagram_accounts(
            self,
            access_token: str,
    ) -> list[dict]:

        response = await self.client.get(
            f"{self.META_GRAPH_URL}/me/accounts",
            params={
                "fields": (
                    "id,"
                    "name,"
                    "instagram_business_account"
                ),
                "access_token": access_token,
            },
        )

        response.raise_for_status()

        pages = response.json().get("data", [])

        instagram_accounts = []

        for page in pages:

            instagram_business_account = (
                page.get("instagram_business_account")
            )

            if not instagram_business_account:
                continue

            instagram_id = instagram_business_account.get("id")

            if not instagram_id:
                continue

            instagram = await self._get_instagram_account(
                instagram_id=instagram_id,
                access_token=access_token,
            )

            instagram_accounts.append(instagram)

        return instagram_accounts

    async def _get_instagram_account(
            self,
            instagram_id: str,
            access_token: str,
    ) -> dict:

        response = await self.client.get(
            f"{self.META_GRAPH_URL}/{instagram_id}",
            params={
                "fields": "id,username,name,profile_picture_url",
                "access_token": access_token,
            },
        )

        response.raise_for_status()

        return response.json()
    async def _exchange_code(
            self,
            code: str,
    ) -> dict:

        response = await self.client.get(
            f"{self.META_GRAPH_URL}/oauth/access_token",
            params={
                "client_id": settings.META_APP_ID,
                "client_secret": settings.META_APP_SECRET,
                "code": code,
            },
        )

        response.raise_for_status()

        return response.json()

    async def _get_waba(
            self,
            waba_id: str,
            access_token: str,
    ) -> dict:

        response = await self.client.get(
            f"{self.META_GRAPH_URL}/{waba_id}",
            params={
                "fields": "id,name",
                "access_token": access_token,
            },
        )

        response.raise_for_status()

        return response.json()

    async def _get_phone_numbers(
            self,
            waba_id: str,
            access_token: str,
    ) -> list[dict]:

        response = await self.client.get(
            f"{self.META_GRAPH_URL}/{waba_id}/phone_numbers",
            params={
                "fields": (
                    "id,"
                    "display_phone_number,"
                    "verified_name,"
                    "quality_rating"
                ),
                "access_token": access_token,
            },
        )

        response.raise_for_status()

        data = response.json()

        return data.get("data", [])

    async def _get_phone_number(
            self,
            phone_number_id: str,
            access_token: str,
    ) -> dict:

        response = await self.client.get(
            f"{self.META_GRAPH_URL}/{phone_number_id}",
            params={
                "fields": (
                    "id,"
                    "display_phone_number,"
                    "verified_name,"
                    "quality_rating"
                ),
                "access_token": access_token,
            },
        )

        response.raise_for_status()

        return response.json()

    async def _get_businesses(
            self,
            access_token: str,
    ) -> list[dict]:

        response = await self.client.get(
            f"{self.META_GRAPH_URL}/me/businesses",
            params={
                "fields": "id,name",
                "access_token": access_token,
            },
        )

        response.raise_for_status()

        return response.json().get("data", [])