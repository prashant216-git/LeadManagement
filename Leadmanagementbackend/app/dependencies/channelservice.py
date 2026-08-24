from fastapi import Depends

from app.channel_engine.channelresolver import ChannelResolver
from app.channel_engine.channelservice import ChannelService
from app.channel_engine.engine import ChannelEngine
from app.dependencies.channelengine import get_channel_engine
from app.dependencies.repositories import get_lead_repository, get_channel_connection_repository, \
    get_channel_credential_repository, get_channel_watch_repository, get_channel_master_repository
from app.dependencies.services import get_message_service, get_channel_resolver, get_credential_encryption_service
from app.repositories.ChannelConnectionRepository import ChannelConnectionRepository
from app.repositories.ChannelCredentialRepository import ChannelCredentialRepository
from app.repositories.ChannelMasterRepositories import ChannelMasterRepository
from app.repositories.ChannelWatchRepository import ChannelWatchRepository
from app.repositories.LeadRepository import LeadRepository
from app.services.CredentialEncryptionService import CredentialEncryptionService
from app.services.messageservice import MessageService


def get_channel_service(
    channel_engine: ChannelEngine = Depends(
        get_channel_engine
    ),
    connection_repository: ChannelConnectionRepository = Depends(
        get_channel_connection_repository
    ),
    channel_master_repository: ChannelMasterRepository = Depends(
        get_channel_master_repository
    ),
    credential_repository: ChannelCredentialRepository = Depends(
        get_channel_credential_repository
    ),
    credential_service: CredentialEncryptionService = Depends(
        get_credential_encryption_service
    ),
    channel_watch_repository: ChannelWatchRepository = Depends(
        get_channel_watch_repository
    ),
    channel_resolver: ChannelResolver = Depends(
        get_channel_resolver
    ),
    lead_repository: LeadRepository = Depends(
        get_lead_repository
    ),
) -> ChannelService:

    return ChannelService(
        channel_engine=channel_engine,
        connection_repository=connection_repository,
        channel_master_repository=channel_master_repository,
        credentials_repository=credential_repository,
        credential_encryption_service=credential_service,
        channel_watch_repository=channel_watch_repository,
        channel_resolver=channel_resolver,
        lead_repository=lead_repository,
    )