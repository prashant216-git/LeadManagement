from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.channel_engine.engine import ChannelEngine
from app.db.session import get_db
from app.dependencies.channelengine import get_channel_engine
from app.dependencies.repositories import get_channel_master_repository
from app.repositories.ChannelConnectionRepository import ChannelConnectionRepository
from app.repositories.ChannelMasterRepositories import ChannelMasterRepository
from app.repositories.LeadRepository import LeadRepository
from app.services.MeetingService import MeetingService


def get_meeting_service(
    db: AsyncSession = Depends(get_db),
    channel_engine: ChannelEngine = Depends(get_channel_engine),
channel_master_repository : ChannelMasterRepository =Depends(get_channel_master_repository)
) -> MeetingService:

    lead_repository = LeadRepository(db)

    channel_connection_repository = ChannelConnectionRepository(
        db
    )



    return MeetingService(
        db=db,
        channel_engine=channel_engine,
        lead_repository=lead_repository,
        channel_connection_repository=channel_connection_repository,
        channel_master_repository=channel_master_repository

    )