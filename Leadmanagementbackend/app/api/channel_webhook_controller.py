from fastapi import APIRouter, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.channel_engine.channelservice import ChannelService
from app.channel_engine.engine import ChannelEngine
from app.db.session import get_db
from app.repositories.ChannelConnectionRepository import ChannelConnectionRepository
from app.repositories.ChannelCredentialRepository import ChannelCredentialRepository
from app.repositories.ChannelMasterRepositories import ChannelMasterRepository
from app.repositories.ChannelWatchRepository import ChannelWatchRepository
from app.repositories.LeadRepository import LeadRepository
from app.repositories.MessageRepository import MessageRepository
from app.services.CredentialEncryptionService import CredentialEncryptionService
from app.services.Leadmanagementservice import LeadService
from app.channel_engine.channelresolver import ChannelResolver
from app.services.messageservice import MessageService

router = APIRouter(
    prefix="/webhooks",
    tags=["Channel Webhooks"],
)

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
    lead_repository = LeadRepository(db)
    credential_service = CredentialEncryptionService()
    message_repository = MessageRepository(db)
    message_repository=message_repository, lead_repository=LeadRepository(db)


    channel_watch_repository=ChannelWatchRepository(db)




    channel_resolver=ChannelResolver(connection_repository=connection_repository,
        credential_repository=credential_repository,
        channel_watch_repository=channel_watch_repository,
        channel_master_repository=channel_master_repository,
        credential_encryption_service=credential_service,message_repository=message_repository)


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
        channel_resolver=channel_resolver,
        message_service=message_service




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
@router.post("/{channel_code}")
async def channel_webhook(
    channel_code: str,
    request: Request,
channel_service: ChannelService = Depends(
        get_channel_service
    ),
):
    payload = await request.json()

    print("CHANNEL:", channel_code)
    print("PUBSUB BODY:", payload)
    return await channel_service.handle_notification(
        channel_code=channel_code,
        payload=payload,
    )

