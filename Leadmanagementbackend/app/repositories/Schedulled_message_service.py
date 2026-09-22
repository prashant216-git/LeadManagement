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
    ) -> ScheduledMessage | None:

        statement = (
            select(ScheduledMessage)
            .where(
                ScheduledMessage.id == scheduled_message_id
            )
        )

        return self.db.execute(
            statement
        ).scalar_one_or_none()

    def update(
        self,
        scheduled_message: ScheduledMessage,
    ) -> ScheduledMessage:

        self.db.commit()
        self.db.refresh(scheduled_message)

        return scheduled_message