# app/dependencies/repositories.py

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db

from app.repositories.LeadRepository import LeadRepository
from app.repositories.LeadStatusMasterRepository import LeadStatusMasterRepository
from app.repositories.LeadStatusRepository import LeadStatusRepository
from app.repositories.MessageRepository import MessageRepository
from app.repositories.ChannelConnectionRepository import (
    ChannelConnectionRepository,
)
from app.repositories.ChannelMasterRepositories import (
    ChannelMasterRepository,
)
from app.repositories.ChannelCredentialRepository import (
    ChannelCredentialRepository,
)
from app.repositories.ChannelWatchRepository import (
    ChannelWatchRepository,
)
from app.repositories.Scheduled_message_repository import ScheduledMessageRepository
from app.repositories.Userrepositories import UserRepository
from app.repositories.AttachementRepository import AttachmentRepository
from app.repositories.QuickMessageRepository import QuickMessageRepository


def get_lead_repository(
    db: AsyncSession = Depends(get_db),
) -> LeadRepository:
    return LeadRepository(db)


def get_message_repository(
    db: AsyncSession = Depends(get_db),
) -> MessageRepository:
    return MessageRepository(db)


def get_channel_connection_repository(
    db: AsyncSession = Depends(get_db),
) -> ChannelConnectionRepository:
    return ChannelConnectionRepository(db)


def get_channel_master_repository(
    db: AsyncSession = Depends(get_db),
) -> ChannelMasterRepository:
    return ChannelMasterRepository(db)


def get_channel_credential_repository(
    db: AsyncSession = Depends(get_db),
) -> ChannelCredentialRepository:
    return ChannelCredentialRepository(db)


def get_channel_watch_repository(
    db: AsyncSession = Depends(get_db),
) -> ChannelWatchRepository:
    return ChannelWatchRepository(db)

def get_user_repository(
    db: AsyncSession = Depends(get_db),
):
    return UserRepository(db)

def get_lead_status_repository(
    db: AsyncSession = Depends(get_db),
):
    return LeadStatusRepository(db)

def get_lead_status_master_repository(
db: AsyncSession = Depends(get_db),
):
    return LeadStatusMasterRepository(db)
def get_scheduled_message_repository(db: AsyncSession = Depends(get_db)):
    return ScheduledMessageRepository(db)

def get_quick_message_repository(
    db: AsyncSession = Depends(get_db),
) -> QuickMessageRepository:

    return QuickMessageRepository(db)


def get_attachment_repository(
    db: AsyncSession = Depends(get_db),
) -> AttachmentRepository:

    return AttachmentRepository(db)