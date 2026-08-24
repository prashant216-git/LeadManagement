# app/dependencies/repositories.py

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db

from app.repositories.LeadRepository import LeadRepository
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