from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import PlainTextResponse

from app.channel_engine.channelservice import ChannelService
from app.core.config import settings
from app.dependencies.channelservice import get_channel_service


router = APIRouter(
    prefix="/webhooks",
    tags=["Channel Webhooks"],
)


@router.api_route(
    "/{channel_code}",
    methods=["GET", "POST"],
)
async def channel_webhook(
    channel_code: str,
    request: Request,
    channel_service: ChannelService = Depends(
        get_channel_service
    ),
):
    try:

        # ==================================================
        # GET → WEBHOOK VERIFICATION
        # ==================================================
        print("slivng webhook")

        if request.method == "GET":
            query_params = dict(
                request.query_params
            )

            return await channel_service.verify_webhook(
                channel_code=channel_code,
                query_params=query_params,
            )

        # ==================================================
        # POST → WEBHOOK EVENT
        # ==================================================

        payload = await request.json()

        print(
            "CHANNEL:",
            channel_code,
        )

        print(
            "WEBHOOK BODY:",
            payload,
        )

        return await channel_service.handle_notification(
            channel_code=channel_code,
            payload=payload,
        )


    except Exception as e:

        print(

            f"Webhook failed [{channel_code}]: {repr(e)}"

        )

        raise