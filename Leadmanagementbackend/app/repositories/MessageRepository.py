from app.models.messages import Message

from sqlalchemy import select
class MessageRepository:

    def __init__(self, db):
        self.db = db

    def create(
        self,
        message: Message,
    ) -> Message:

        self.db.add(message)

        self.db.commit()

        self.db.refresh(message)

        return message

    def get_by_provider_message_id_and_lead_id(
            self,
            provider_message_id: str,
            lead_id: int,
    ) -> Message | None:
        result = self.db.execute(
            select(Message)
            .where(
                Message.provider_message_id == provider_message_id,
                Message.lead_id == lead_id,
            )
        )

        return result.scalar_one_or_none()