from urllib.parse import urlencode

import httpx

from app.DTOs.connection.callbackerror import CallbackException, CallbackError
from app.DTOs.connection.connection_request import ConnectRequest
from app.DTOs.connection.connection_response import ConnectResponse
from app.channel_engine.BaseChannelProvider import BaseChannelProvider
from app.channel_engine.registry import ChannelProviderRegistry
from app.core.config import settings
from app.enums.channel import ConnectionStatus


@ChannelProviderRegistry.register("whatsapp")
class WhatsappProvider(BaseChannelProvider):

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
            db

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
                "WhatsApp channel already connected."
            )

        return ConnectResponse(
            success=True,
            config_id=settings.META_EMBEDDED_SIGNUP_CONFIG_ID,
            message="Start WhatsApp Embedded Signup.",
            state=state,
        )

    async def handle_callback(
            self,
            query_params: dict,
            headers: dict,
            body: dict,
    ):
        """
        Handle WhatsApp Embedded Signup callback.

        The frontend sends the Meta Embedded Signup result along
        with the connection state.

        The provider is responsible for interpreting the Meta
        payload and returning a normalized connection result.
        """

        # ---------------------------------------------------------
        # 1. Validate request body
        # ---------------------------------------------------------

        if not body:
            raise CallbackException(
                CallbackError(
                    message="WhatsApp callback body is missing.",
                    state=None,
                )
            )

        # ---------------------------------------------------------
        # 2. Extract state
        # ---------------------------------------------------------

        state = body.get("state")

        if not state:
            raise CallbackException(
                CallbackError(
                    message="WhatsApp OAuth state is missing.",
                    state=None,
                )
            )

        # ---------------------------------------------------------
        # 3. Extract Meta payload
        # ---------------------------------------------------------

        payload = body.get("payload")

        if not payload:
            raise CallbackException(
                CallbackError(
                    message="WhatsApp callback payload is missing.",
                    state=state,
                )
            )

        # ---------------------------------------------------------
        # 4. Handle Meta error
        # ---------------------------------------------------------

        error = payload.get("error")

        if error:
            raise CallbackException(
                CallbackError(
                    message=str(error),
                    state=state,
                )
            )

        # ---------------------------------------------------------
        # 5. Extract access token
        # ---------------------------------------------------------

        access_token = payload.get("access_token")

        if not access_token:
            raise CallbackException(
                CallbackError(
                    message="WhatsApp access token is missing.",
                    state=state,
                )
            )

        # ---------------------------------------------------------
        # 6. Extract WABA ID
        # ---------------------------------------------------------

        waba_id = payload.get("waba_id")

        if not waba_id:
            raise CallbackException(
                CallbackError(
                    message=(
                        "WhatsApp Business Account ID "
                        "is missing."
                    ),
                    state=state,
                )
            )

        # ---------------------------------------------------------
        # 7. Extract Phone Number ID
        # ---------------------------------------------------------

        phone_number_id = payload.get("phone_number_id")

        if not phone_number_id:
            raise CallbackException(
                CallbackError(
                    message=(
                        "WhatsApp phone number ID "
                        "is missing."
                    ),
                    state=state,
                )
            )

        # ---------------------------------------------------------
        # 8. Get phone information from Meta
        # ---------------------------------------------------------

        phone_number = await self._get_phone_number(
            phone_number_id=phone_number_id,
            access_token=access_token,
        )

        display_phone_number = (
            phone_number.get("display_phone_number")
        )

        verified_name = phone_number.get(
            "verified_name"
        )

        # ---------------------------------------------------------
        # 9. Return normalized provider result
        # ---------------------------------------------------------

        return {
            "state": state,

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

            "credentials": {
                "access_token": access_token,
                "refresh_token": None,
                "token_type": "Bearer",
            },
        }

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