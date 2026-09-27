from uuid import UUID

from sqlalchemy import select


from app.models.scheduled_message import ScheduledMessage



class ScheduledMessageRepository:

    def __init__(self, db):
        self.db = db

    def create(
        self,
        scheduled_message: ScheduledMessage,
    ) -> ScheduledMessage:

        self.db.add(scheduled_message)
        self.db.commit()
        self.db.refresh(scheduled_message)

        return scheduled_message

    def get_by_id(
        self,
        scheduled_message_id: UUID,
            user_id: UUID,
    ) -> ScheduledMessage | None:

        statement = (
            select(ScheduledMessage)
            .where(
                ScheduledMessage.id == scheduled_message_id , ScheduledMessage.user_id==user_id
            )
        )

        return self.db.execute(
            statement
        ).scalar_one_or_none()

    def get_by_lead_id_all(self, lead_id: UUID) -> list[ScheduledMessage] | None:
        statement = (select(ScheduledMessage).where(ScheduledMessage.lead_id==lead_id, ))
        result =self.db.execute(statement)

        return list(result.scalars().all())




    def update(
        self,
        scheduled_message: ScheduledMessage,
    ) -> ScheduledMessage:

        self.db.commit()
        self.db.refresh(scheduled_message)

        return scheduled_message