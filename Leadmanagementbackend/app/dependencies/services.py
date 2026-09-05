from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.ai_service import AIService
from app.channel_engine.channelresolver import ChannelResolver
from app.db.session import get_db
from app.repositories.ChannelConnectionRepository import ChannelConnectionRepository
from app.repositories.ChannelCredentialRepository import ChannelCredentialRepository
from app.repositories.ChannelMasterRepositories import ChannelMasterRepository
from app.repositories.ChannelWatchRepository import ChannelWatchRepository
from app.repositories.DashboardRepository import DashboardRepository
from app.repositories.SummaryRepository import SummaryRepository
from app.services.Chatservice import ChatService
from app.services.CredentialEncryptionService import (
    CredentialEncryptionService,
)

from app.repositories.LeadRepository import LeadRepository
from app.repositories.MessageRepository import MessageRepository
from app.services.DashboardService import DashboardService
from app.services.Leadmanagementservice import LeadService
from app.services.Summaryservice import SummaryService
from app.services.messageservice import MessageService

from app.dependencies.repositories import (
    get_lead_repository,
    get_message_repository,
    get_channel_connection_repository, get_channel_credential_repository, get_channel_watch_repository,
    get_channel_master_repository,
)
from app.socketmanager.websocketmanager import websocketmanager


def get_credential_encryption_service(
) -> CredentialEncryptionService:
    return CredentialEncryptionService()

def get_message_service(
    message_repository: MessageRepository = Depends(
        get_message_repository
    ),
    lead_repository: LeadRepository = Depends(
        get_lead_repository
    ),
) -> MessageService:

    return MessageService(
        message_repository=message_repository,
        lead_repository=lead_repository,
    )

def get_lead_service(
    lead_repository: LeadRepository = Depends(
        get_lead_repository
    ),
    channel_connection_repository: ChannelConnectionRepository = Depends(
        get_channel_connection_repository
    ),
) -> LeadService:

    return LeadService(
        lead_repository=lead_repository,
        channel_connection_repository=(
            channel_connection_repository
        ),
    )

def get_chat_service(
    lead_repository: LeadRepository = Depends(
        get_lead_repository
    ),
    message_repository: MessageRepository = Depends(
        get_message_repository
    ),
) -> ChatService:

    return ChatService(
        lead_repository=lead_repository,
        message_repository=message_repository,
    )

def get_dashboard_service(
    db: AsyncSession = Depends(get_db),
) -> DashboardService:

    dashboard_repository = DashboardRepository(
        db
    )

    return DashboardService(
        dashboard_repository=dashboard_repository
    )


def get_channel_resolver(
    connection_repository: ChannelConnectionRepository = Depends(
        get_channel_connection_repository
    ),
    credential_repository: ChannelCredentialRepository = Depends(
        get_channel_credential_repository
    ),
    channel_watch_repository: ChannelWatchRepository = Depends(
        get_channel_watch_repository
    ),
    channel_master_repository: ChannelMasterRepository = Depends(
        get_channel_master_repository
    ),
    credential_service: CredentialEncryptionService = Depends(
        get_credential_encryption_service
    ),
    message_repository: MessageRepository = Depends(
        get_message_repository
    ),
) -> ChannelResolver:

    return ChannelResolver(
        connection_repository=connection_repository,
        credential_repository=credential_repository,
        channel_watch_repository=channel_watch_repository,
        channel_master_repository=channel_master_repository,
        credential_encryption_service=credential_service,
        message_repository=message_repository,
    )

def get_ai_service(
    db: AsyncSession = Depends(get_db),
    message_service: MessageService = Depends(get_message_service),
    channel_resolver: ChannelResolver = Depends(get_channel_resolver),
) -> AIService:

    return AIService(
        db=db,
        messageservice=message_service,
        channel_resolver=channel_resolver,
    )
def get_summary_service(
    db: AsyncSession = Depends(get_db),
    ai_service: AIService = Depends(get_ai_service),
) -> SummaryService:

    message_repo = MessageRepository(db)
    summary_repo = SummaryRepository(db)

    return SummaryService(
        message_repo=message_repo,
        summary_repo=summary_repo,
        ai_service=ai_service,
    )

websocket_manager = websocketmanager()


def get_websocket_manager() -> websocketmanager:
    print("MANAGER:", id(websocket_manager))
    return websocket_manager

