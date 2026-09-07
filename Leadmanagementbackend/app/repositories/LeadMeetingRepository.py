from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.lead_meeting import LeadMeeting


class LeadMeetingRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        meeting: LeadMeeting,
    ) -> LeadMeeting:

        self.db.add(meeting)
        self.db.commit()
        self.db.refresh(meeting)

        return meeting

    def get_by_id(
        self,
        meeting_id: UUID,
    ) -> LeadMeeting | None:

        statement = (
            select(LeadMeeting)
            .where(LeadMeeting.id == meeting_id)
        )

        result = self.db.execute(statement)

        return result.scalar_one_or_none()

    def get_by_provider_event_id(
        self,
        provider_event_id: str,
    ) -> LeadMeeting | None:

        statement = (
            select(LeadMeeting)
            .where(
                LeadMeeting.provider_event_id
                == provider_event_id
            )
        )

        result = self.db.execute(statement)

        return result.scalar_one_or_none()

    def get_by_lead_id(
        self,
        lead_id: UUID,
    ) -> list[LeadMeeting]:

        statement = (
            select(LeadMeeting)
            .where(LeadMeeting.lead_id == lead_id)
            .order_by(LeadMeeting.start_time.desc())
        )

        result = self.db.execute(statement)

        return list(result.scalars().all())


    def save(self, meeting: LeadMeeting) -> LeadMeeting:
        self.db.add(meeting)
        self.db.flush()
        return meeting