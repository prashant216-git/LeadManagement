from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, HTTPException, Request
from starlette.responses import RedirectResponse

from app.DTOs.channelreponseDTO import ChannelResponseDTO
from app.DTOs.connection.connection_response import ConnectResponse
from app.channel_engine.channelresolver import ChannelResolver
from app.channel_engine.engine import ChannelEngine
from app.channel_engine.channelservice import ChannelService
from app.core.config import settings

from app.repositories.ChannelConnectionRepository import (
    ChannelConnectionRepository,
)

from app.repositories.ChannelMasterRepositories import (
    ChannelMasterRepository,
)

from app.repositories.ChannelCredentialRepository import (
    ChannelCredentialRepository,
)
from app.repositories.ChannelWatchRepository import ChannelWatchRepository
from app.repositories.LeadRepository import LeadRepository

from app.services.CredentialEncryptionService import (
    CredentialEncryptionService,
)

from app.db.session import get_db


router = APIRouter(
    prefix="/channels",
    tags=["Channels"],
)


# ==========================================================
# CHANNEL SERVICE
# ==========================================================

def get_channel_service(
    db: AsyncSession = Depends(get_db),
) -> ChannelService:

    # ------------------------------------------------------
    # Repositories
    # ------------------------------------------------------

    connection_repository = ChannelConnectionRepository(
        db
    )

    channel_master_repository = ChannelMasterRepository(
        db
    )

    credential_repository = ChannelCredentialRepository(
        db
    )

    # ------------------------------------------------------
    # Credential service
    # ------------------------------------------------------

    credential_service = CredentialEncryptionService()

    channel_watch_repository=ChannelWatchRepository(db)

    lead_repository = LeadRepository(db)

    channel_resolver = ChannelResolver(connection_repository=connection_repository,
                                       credential_repository=credential_repository,
                                       channel_watch_repository=channel_watch_repository,
                                       channel_master_repository=channel_master_repository,
                                       credential_encryption_service=credential_service, )

    # ------------------------------------------------------
    # Channel Engine
    # ------------------------------------------------------

    channel_engine = ChannelEngine(
        connection_repository=connection_repository,
        credential_repository=credential_repository,
        credential_service=credential_service,
        channel_watch_repository=channel_watch_repository,
        channel_master_repository=channel_master_repository,
        lead_repository=lead_repository,
        channel_resolver=channel_resolver


    )

    # ------------------------------------------------------
    # Channel Service
    # ------------------------------------------------------

    return ChannelService(
        channel_engine=channel_engine,
        connection_repository=connection_repository,
        channel_master_repository=channel_master_repository,
        credentials_repository=credential_repository,
        credential_encryption_service=credential_service,
        channel_watch_repository=channel_watch_repository,
        channel_resolver=channel_resolver,


    )


# ==========================================================
# CONNECT CHANNEL
# ==========================================================

@router.post(
    "/{channel_code}/connect",
    response_model=ConnectResponse,
)
async def connect_channel(
    channel_code: str,
    channel_service: ChannelService = Depends(
        get_channel_service
    ),
):

    # ======================================================
    # TEMPORARY TEST TENANT
    # ======================================================
    #
    # Later:
    #
    # tenant_id = current_user.tenant_id
    #
    # For now we always use tenant 1.
    #

    tenant_id = 1
    print(settings.GOOGLE_CLIENT_ID)
    try:

        return await channel_service.connect(
            tenant_id=tenant_id,
            channel_code=channel_code,
        )

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except Exception as e:

        print(
            f"Channel connection failed: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to connect channel.",
        )

@router.api_route(
    "/{channel_code}/callback",
    methods=["GET", "POST"],
)
async def channel_callback(
    channel_code: str,
    request: Request,
channel_service: ChannelService = Depends(
        get_channel_service
    ),
):
    try:
        # --------------------------------------------------
        # Query parameters
        # --------------------------------------------------

        query_params = dict(request.query_params)

        # --------------------------------------------------
        # Headers
        # --------------------------------------------------

        headers = dict(request.headers)

        # --------------------------------------------------
        # Body
        # --------------------------------------------------

        body = None

        if request.method == "POST":
            content_type = request.headers.get(
                "content-type",
                "",
            )

            if "application/json" in content_type:
                body = await request.json()

            else:
                body = await request.body()

        # --------------------------------------------------
        # Pass EVERYTHING to ChannelService
        # --------------------------------------------------
        rs=await channel_service.handle_callback(channel_code=channel_code, body=body,headers=headers,query_params=query_params)
        print(rs)



        return RedirectResponse(
            url=(
                "https://veloratechnologies.in/"
                "channel-configuration"
                "?channel=gmail"
                "&status=connected"
            )
        )

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

@router.post(
    "/gmail/setup-watch",
)
async def setup_gmail_watch(
    request: Request,
identifier: str = Body(..., embed=True),
channel_service: ChannelService = Depends(
        get_channel_service
    ),
):
    try:
        # Temporary tenant for testing
        tenant_id = 1

        return await channel_service.setup_watch(identifier=identifier,
            tenant_id=tenant_id,channel_code="gmail"
        )

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )
@router.get(
    "/all",
    response_model=list[ChannelResponseDTO]
)
async def get_all_channels(
    service: ChannelService = Depends(get_channel_service),
):
    try:
        tenant_id=1
        return await service.get_all_channels(tenant_id=tenant_id)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


@router.post(
    "/{connection_id}/disconnect",
)
async def disconnect_channel(
    connection_id: int,
    channel_service: ChannelService = Depends(
        get_channel_service
    ),
):

    try:

        return await channel_service.disconnect(
            connection_id=connection_id,
        )

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except Exception as e:

        print(
            f"Channel disconnect failed: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to disconnect channel.",
        )
