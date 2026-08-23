from app.models import Lead
from app.models.channel_connection import ChannelConnection
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
            channel_connection_id:int,
            lead_id: int,
    ) -> Message | None:
        result = self.db.execute(
            select(Message)
            .where(
                Message.provider_message_id == provider_message_id,
                Message.lead_id == lead_id, Message.channel_connection_id == channel_connection_id
            )
        )

        return result.scalar_one_or_none()

    def get_messages_by_lead_id_and_channel_id(
            self,
            lead_id: int,
            channel_id: int,
    ) -> list[Message]:
        statement = (
            select(Message)
            .join(
                Lead,
                Message.lead_id == Lead.id,
            )
            .where(
                Lead.id == lead_id,
                Lead.source_channel_id == channel_id,
            )
            .order_by(
                Message.provider_created_at.asc()
            )
        )

        result = self.db.execute(
            statement
        )

        return result.scalars().all()

    from sqlalchemy import select

    def get_by_provider_message_id(
            self,
            provider_message_id: str,
    ):
        result = self.db.execute(
            select(Message).where(
                Message.provider_message_id
                == provider_message_id
            )
        )

        return result.scalar_one_or_none()

    def get_by_id(
            self,
            message_id: int,
    ) -> Message | None:
        statement = (
            select(Message)
            .where(
                Message.id == message_id
            )
        )

        result = self.db.execute(
            statement
        )

        return result.scalar_one_or_none()