from sqlalchemy.orm import Session

from app.models.messages import Message


class MessageService:

    @staticmethod
    def save_message(
        db: Session,
        user_id: int,
        channel: str,
        sender: str,
        content: str,
        channel_message_id: str | None = None,
        message_type: str = "text",
    message_timestamp: int | None = None

    ) -> Message:

        message = Message(
            user_id=user_id,
            channel=channel,
            channel_message_id=channel_message_id,
            sender=sender,
            message_type=message_type,
            content=content,
            message_timestamp=message_timestamp
        )

        db.add(message)
        db.commit()
        db.refresh(message)

        return message

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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