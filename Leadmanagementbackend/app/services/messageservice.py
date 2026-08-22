from datetime import datetime

from sqlalchemy.orm import Session

from app.models.messages import Message
from app.repositories.MessageRepository import MessageRepository

from app.enums.message import MessageDirection
from app.enums.message import MessageType


class MessageService:

    def __init__(
            self,
            message_repository: MessageRepository,
    ):
        self.message_repository = (
            message_repository
        )

    async def create_message(
            self,
            lead_id: int | None,
            channel_connection_id: int | None,
            provider_message_id: str | None = None,
            direction: MessageDirection | None = None,
            sender_identifier: str | None = None,
            recipient_identifier: str | None = None,
            content: str | None = None,
            message_type: MessageType | None = None,
            provider_created_at: datetime | None = None,
            provider_metadata: dict | None = None,
    ) -> Message:

        existmessage=self.message_repository.get_by_provider_message_id_and_lead_id(provider_message_id=provider_message_id, lead_id=lead_id)
        if existmessage:
            return existmessage


        message = Message(
            lead_id=lead_id,
            channel_connection_id=channel_connection_id,
            provider_message_id=provider_message_id,
            direction=direction,
            sender_identifier=sender_identifier,
            recipient_identifier=recipient_identifier,
            content=content,
            message_type=message_type,
            provider_created_at=provider_created_at,
            provider_metadata=provider_metadata,
        )

        return self.message_repository.create(
            message
        )



    


    def get_latest_message(
        db: Session,
        user_id: int
    ) -> Message | None:

        return (
            db.query(Message)
            .filter(Message.user_id == user_id)
            .order_by(Message.created_at.desc())
            .first()
        )


    def get_recent_messages(
        db: Session,
        user_id: int,
        limit: int = 5
    ) -> list[Message]:

        messages = (
            db.query(Message)
            .filter(Message.user_id == user_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
            .all()
        )

        return list(reversed(messages))


    def get_all_messages(
        db: Session,
        user_id: int
    ) -> list[Message]:

        return (
            db.query(Message)
            .filter(Message.user_id == user_id)
            .order_by(Message.created_at.asc())
            .all()
        )

    @staticmethod
    def get_message_by_channel_message_id(
        db: Session,
        channel_message_id: str
    ) -> Message | None:

        return (
            db.query(Message)
            .filter(
                Message.channel_message_id == channel_message_id
            )
            .first()
        )

    @staticmethod
    def message_exists(
        db: Session,
        channel_message_id: str
    ) -> bool:

        return (
            db.query(Message)
            .filter(
                Message.channel_message_id == channel_message_id
            )
            .first()
            is not None
        )

    @staticmethod
    def get_all_messages(
            db,
            user_id: int
    ):
        return (
            db.query(Message)
            .filter(
                Message.user_id == user_id
            )
            .order_by(
                Message.id.asc()
            )
            .all()
        )

    @staticmethod
    def get_messages_after_id(
            db,
            user_id: int,
            message_id: int
    ):
        return (
            db.query(Message)
            .filter(
                Message.user_id == user_id,
                Message.id > message_id
            )
            .order_by(
                Message.id.asc()
            )
            .all()
        )