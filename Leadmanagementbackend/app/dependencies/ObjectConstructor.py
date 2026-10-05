from sqlalchemy.ext.asyncio import AsyncSession

from app.channel_engine.channelresolver import ChannelResolver
from app.channel_engine.channelservice import ChannelService
from app.channel_engine.engine import ChannelEngine

from app.repositories.ChannelConnectionRepository import ChannelConnectionRepository
from app.repositories.ChannelCredentialRepository import ChannelCredentialRepository
from app.repositories.ChannelMasterRepositories import ChannelMasterRepository
from app.repositories.ChannelWatchRepository import ChannelWatchRepository
from app.repositories.LeadRepository import LeadRepository
from app.repositories.LeadStatusMasterRepository import LeadStatusMasterRepository
from app.repositories.LeadStatusRepository import LeadStatusRepository
from app.repositories.MessageRepository import MessageRepository
from app.services.CredentialEncryptionService import CredentialEncryptionService
from app.services.Leadmanagementservice import LeadService
from app.services.messageservice import MessageService
from app.socketmanager.websocketmanager import websocketmanager
from app.repositories.AttachementRepository import AttachmentRepository
from app.services.AttachementService import AttachmentService
from app.repositories.LeadStatusHistoryRepository import LeadStatusHistoryRepository
from app.repositories.LeadTransferHistoryRepository import LeadTransferHistoryRepository


def build_channel_service(db: AsyncSession) -> ChannelService:
    connection_repository = ChannelConnectionRepository(db)
    credential_repository = ChannelCredentialRepository(db)
    channel_master_repository = ChannelMasterRepository(db)
    channel_watch_repository = ChannelWatchRepository(db)
    lead_repository = LeadRepository(db)
    lead_status_repository = LeadStatusRepository(db)
    lead_status_master_repository = LeadStatusMasterRepository(db)
    attachement_repository = AttachmentRepository(db)

    attachement_service = AttachmentService()

    credential_service = CredentialEncryptionService()

    message_repository = MessageRepository(db)
    message_service = MessageService(
        message_repository=message_repository,
        lead_repository=lead_repository,
        attachment_repository=attachement_repository,
        db=db
    )
    websocket_manager = websocketmanager()

    channel_resolver = ChannelResolver(
        connection_repository=connection_repository,
        credential_repository=credential_repository,
        channel_watch_repository=channel_watch_repository,
        channel_master_repository=channel_master_repository,
        credential_encryption_service=credential_service,
        message_repository=message_repository,
        attachement_repository=attachement_repository,
        attachement_service=attachement_service
    )

    lead_service = LeadService(
        lead_repository=lead_repository,
        channel_connection_repository=connection_repository,
        # ...
        lead_status_master_repository=lead_status_master_repository,
        lead_status_repository=lead_status_repository,
    status_history_repository=LeadStatusHistoryRepository(db),
    lead_transfer_history_repository=LeadTransferHistoryRepository(db)
    )

    channel_engine = ChannelEngine(
        connection_repository=connection_repository,
        credential_repository=credential_repository,
        credential_service=credential_service,
        channel_watch_repository=channel_watch_repository,
        channel_master_repository=channel_master_repository,
        lead_repository=lead_repository,
        channel_resolver=channel_resolver,
        message_service=message_service,
        db=db,
        webmanager=websocket_manager,
        lead_service=lead_service,
    )

    return ChannelService(
        db=db,
        channel_engine=channel_engine,
        connection_repository=connection_repository,
        channel_master_repository=channel_master_repository,
        credentials_repository=credential_repository,
        credential_encryption_service=credential_service,
        channel_watch_repository=channel_watch_repository,
        channel_resolver=channel_resolver,
        lead_repository=lead_repository,
    )