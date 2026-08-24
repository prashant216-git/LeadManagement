from fastapi import APIRouter, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.channel_engine.channelservice import ChannelService
from app.channel_engine.engine import ChannelEngine
from app.db.session import get_db
from app.dependencies.channelservice import get_channel_service
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

