from datetime import datetime
from uuid import UUID

from app.models.lead_meeting import LeadMeeting
from app.repositories.ChannelMasterRepositories import ChannelMasterRepository
from app.repositories.LeadMeetingRepository import (
    LeadMeetingRepository,
)


class MeetingService:

    def __init__(
        self,
        db,
        channel_engine,
        lead_repository,
        channel_connection_repository,
            channel_master_repository: ChannelMasterRepository,
    ):
        self.db = db
        self.channel_engine = channel_engine
        self.lead_repository = lead_repository
        self.channel_connection_repository = (
            channel_connection_repository

        )
        self.channel_master_repository = channel_master_repository


        self.meeting_repository = LeadMeetingRepository(db)

    async def create_meeting(
            self,
            lead_id: UUID,
            channel_connection_id: UUID,
            title: str,
            description: str | None,
            start_time: datetime,
            end_time: datetime,
    ) -> LeadMeeting:

        lead = self.lead_repository.get_by_id(
            lead_id=lead_id
        )

        if lead is None:
            raise ValueError("Lead not found.")

        connection = (
            self.channel_connection_repository
            .get_by_id(channel_connection_id)
        )

        channel=self.channel_master_repository.get_by_id(connection.channel_id)

        if connection is None:
            raise ValueError("Channel connection not found.")

        if connection.connection_status != "CONNECTED":
            raise ValueError(
                "Channel connection is not connected."
            )

        if connection.channel.code != "gmail":
            raise ValueError(
                "Meeting creation is not supported for this channel."
            )

        if not lead.email:
            raise ValueError(
                "Lead does not have an email address."
            )

        provider = self.channel_engine.create_provider(

            channel_code=channel.code,
        )

        result =await provider.create_meeting(
            title=title,
            connection_id=channel_connection_id,
            description=description,
            start_time=start_time,
            end_time=end_time,
            attendee_email=lead.email,
        )

        meeting = LeadMeeting(
            lead_id=lead_id,
            channel_connection_id=channel_connection_id,
            provider_event_id=result["event_id"],
            title=title,
            description=description,
            start_time=start_time,
            end_time=end_time,
            meeting_link=result["meeting_link"],
            status="SCHEDULED",
        )

        try:
            result=self.meeting_repository.save(meeting)
            self.db.commit()
            return result


        except Exception:
            self.db.rollback()
            raise

    async def get_meetings_by_lead_id(
            self,
            lead_id: UUID,
    ) -> list[LeadMeeting]:

        lead = self.lead_repository.get_by_id(
            lead_id=lead_id
        )

        if lead is None:
            raise ValueError("Lead not found.")

        return self.meeting_repository.get_by_lead_id(
            lead_id=lead_id
        )
