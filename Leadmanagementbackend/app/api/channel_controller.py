from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.DTOs.connection.connection_response import ConnectResponse

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

    # ------------------------------------------------------
    # Channel Engine
    # ------------------------------------------------------

    channel_engine = ChannelEngine(
        connection_repository=connection_repository,
        credential_repository=credential_repository,
        credential_service=credential_service,
    )

    # ------------------------------------------------------
    # Channel Service
    # ------------------------------------------------------

    return ChannelService(
        channel_engine=channel_engine,
        connection_repository=connection_repository,
        channel_master_repository=channel_master_repository,
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