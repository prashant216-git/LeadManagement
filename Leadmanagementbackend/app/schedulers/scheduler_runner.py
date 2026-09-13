import asyncio

from app.db.session import SessionLocal

from app.channel_engine.channelresolver import ChannelResolver
from app.channel_engine.engine import ChannelEngine

from app.repositories.ChannelConnectionRepository import (
    ChannelConnectionRepository,
)
from app.repositories.ChannelCredentialRepository import (
    ChannelCredentialRepository,
)
from app.repositories.ChannelMasterRepositories import (
    ChannelMasterRepository,
)
from app.repositories.ChannelWatchRepository import (
    ChannelWatchRepository,
)
from app.repositories.LeadRepository import LeadRepository
from app.repositories.MessageRepository import MessageRepository

from app.services.CredentialEncryptionService import (
    CredentialEncryptionService,
)
from app.services.messageservice import MessageService

from app.socketmanager.websocketmanager import websocketmanager

from app.schedulers.gmail_watch_scheduler import (
    GmailWatchScheduler,
)


async def run_schedulers():

    db = SessionLocal()

    try:

        # =========================================
        # Repositories
        # =========================================

        connection_repository = (
            ChannelConnectionRepository(db)
        )

        credential_repository = (
            ChannelCredentialRepository(db)
        )

        watch_repository = (
            ChannelWatchRepository(db)
        )

        channel_master_repository = (
            ChannelMasterRepository(db)
        )

        lead_repository = (
            LeadRepository(db)
        )

        message_repository = (
            MessageRepository(db)
        )

        # =========================================
        # Services
        # =========================================

        credential_service = (
            CredentialEncryptionService()
        )

        # =========================================
        # Channel Resolver
        # =========================================

        channel_resolver = ChannelResolver(
            connection_repository=connection_repository,
            credential_repository=credential_repository,
            channel_watch_repository=watch_repository,
            channel_master_repository=channel_master_repository,
            credential_encryption_service=credential_service,
            message_repository=message_repository,
        )

        # =========================================
        # Message Service
        # =========================================

        message_service = MessageService(
            message_repository=message_repository,
            lead_repository=lead_repository,
        )

        # =========================================
        # WebSocket Manager
        # =========================================

        webmanager = websocketmanager()

        # =========================================
        # Channel Engine
        # =========================================

        channel_engine = ChannelEngine(
            connection_repository=connection_repository,
            credential_repository=credential_repository,
            credential_service=credential_service,
            channel_watch_repository=watch_repository,
            channel_master_repository=channel_master_repository,
            lead_repository=lead_repository,
            channel_resolver=channel_resolver,
            message_service=message_service,
            db=db,
            webmanager=webmanager,
        )

        # =========================================
        # Gmail Watch Scheduler
        # =========================================

        gmail_watch_scheduler = GmailWatchScheduler(
            channel_connection_repository=(
                connection_repository
            ),
            channel_watch_repository=(
                watch_repository
            ),
            channel_engine=channel_engine,
        )

        # =========================================
        # Run Gmail Watch Scheduler
        # =========================================

        await gmail_watch_scheduler.renew_expiring_watches()

    finally:
        await db.close()


if __name__ == "__main__":
    asyncio.run(run_schedulers())