from uuid import UUID

from app.models import Lead, messages
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
            channel_connection_id:UUID,
            lead_id: UUID,
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
            lead_id: UUID,
            channel_id: UUID,
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

    def get_latest_message_by_lead_id(
            self,
            lead_id: UUID,
    ) -> Message | None:
        result = self.db.execute(
            select(Message)
            .where(
                Message.lead_id == lead_id
            )
            .order_by(
                Message.provider_created_at.desc()
            )
            .limit(1)
        )

        return result.scalar_one_or_none()

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
            message_id: UUID,
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

    def get_latest_messages_by_lead_id(
            self,
            lead_id: UUID,
            limit: int = 5,
    ) -> list[Message]:
        statement = (
            select(Message)
            .where(
                Message.lead_id == lead_id
            )
            .order_by(
                Message.created_at.desc()
            )
            .limit(limit)
        )

        result = self.db.execute(statement)

        messages = result.scalars().all()

        return list(reversed(messages))