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

        existing_meeting = self.meeting_repository.get_by_time(lead_id=lead_id,start_time=start_time,end_time=end_time)
        if existing_meeting:
            raise ValueError("Meeting already exists.")

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

        if end_time < start_time:
            raise ValueError("Meeting creation time is before start time.")

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

    async def check_meeting_availability(
            self,
            user_id: UUID,
            start_time: datetime,
            end_time: datetime,
    ) -> bool:

        if end_time <= start_time:
            raise ValueError(
                "End time must be after start time."
            )

        exists = self.meeting_repository.has_overlap(
            user_id=user_id,
            start_time=start_time,
            end_time=end_time,
        )

        return not exists

    async def update_meeting(
            self,
            meeting_id: UUID,
            title: str | None = None,
            description: str | None = None,
            start_time: datetime | None = None,
            end_time: datetime | None = None,
    ) -> LeadMeeting:

        # -------------------------------------------------
        # Get Existing Meeting
        # -------------------------------------------------

        meeting = self.meeting_repository.get_by_id(
            meeting_id=meeting_id
        )

        if meeting is None:
            raise ValueError(
                "Meeting not found."
            )

        # -------------------------------------------------
        # Get Lead
        # -------------------------------------------------

        lead = self.lead_repository.get_by_id(
            lead_id=meeting.lead_id
        )

        if lead is None:
            raise ValueError(
                "Lead not found."
            )

        # -------------------------------------------------
        # Get Connection
        # -------------------------------------------------

        connection = (
            self.channel_connection_repository.get_by_id(
                meeting.channel_connection_id
            )
        )

        if connection is None:
            raise ValueError(
                "Channel connection not found."
            )

        # -------------------------------------------------
        # Validate Connection
        # -------------------------------------------------

        if connection.connection_status != "CONNECTED":
            raise ValueError(
                "Channel connection is not connected."
            )

        if connection.channel.code != "gmail":
            raise ValueError(
                "Meeting update is not supported for this channel."
            )

        # -------------------------------------------------
        # Resolve Updated Values
        # -------------------------------------------------

        updated_title = (
            title
            if title is not None
            else meeting.title
        )

        updated_description = (
            description
            if description is not None
            else meeting.description
        )

        updated_start_time = (
            start_time
            if start_time is not None
            else meeting.start_time
        )

        updated_end_time = (
            end_time
            if end_time is not None
            else meeting.end_time
        )

        # -------------------------------------------------
        # Validate Time
        # -------------------------------------------------

        if updated_end_time <= updated_start_time:
            raise ValueError(
                "End time must be after start time."
            )

        # -------------------------------------------------
        # Check Availability
        # Exclude Current Meeting
        # -------------------------------------------------



        # -------------------------------------------------
        # Get Provider
        # -------------------------------------------------
        channel = self.channel_master_repository.get_by_id(connection.channel_id)

        provider = self.channel_engine.create_provider(

            channel_code=channel.code,
        )

        # -------------------------------------------------
        # Update Google Calendar
        # -------------------------------------------------

        result = await provider.update_meeting(
            connection_id=meeting.channel_connection_id,
            provider_event_id=meeting.provider_event_id,
            title=updated_title,
            description=updated_description,
            start_time=updated_start_time,
            end_time=updated_end_time,
        )

        # -------------------------------------------------
        # Update Local DB
        # -------------------------------------------------

        meeting.title = updated_title
        meeting.description = updated_description
        meeting.start_time = updated_start_time
        meeting.end_time = updated_end_time

        if result.get("meeting_link"):
            meeting.meeting_link = result["meeting_link"]

            result =self.meeting_repository.save(
            meeting
        )
            self.db.commit()

        return result
