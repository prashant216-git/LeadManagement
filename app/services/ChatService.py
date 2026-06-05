from sqlalchemy.orm import Session
from sqlalchemy import func

from app.DTOs.MessageDTO import MessageDTO
from app.DTOs.UserChatDTO import UserChatDTO
from app.models.User import User
from app.models.messages import Message

from app.DTOs.Chats import ChatSidebarDTO


class ChatService:

    @staticmethod
    def get_chat_sidebar(
        db: Session
    ) -> list[ChatSidebarDTO]:

        latest_message_subquery = (

            db.query(
                Message.user_id,
                func.max(Message.created_at)
                .label("latest_time")
            )

            .group_by(Message.user_id)

            .subquery()
        )

        results = (

            db.query(
                User,
                Message
            )

            .outerjoin(
                latest_message_subquery,
                User.id == latest_message_subquery.c.user_id
            )

            .outerjoin(
                Message,
                (Message.user_id == User.id)
                &
                (
                    Message.created_at
                    ==
                    latest_message_subquery.c.latest_time
                )
            )
            .order_by(
                latest_message_subquery.c.latest_time.desc()
            )

            .all()
        )

        return [

            ChatSidebarDTO(
                user_id=user.id,
                name=user.name,
                phone_number=user.phone_number,
                email=user.email,
                latest_message=(
                    message.content
                    if message
                    else None
                ),
                latest_message_time=(
                    str(message.created_at)
                    if message
                    else None
                )
            )

            for user, message in results
        ]

    @staticmethod
    def get_user_chat(
            db: Session,
            user_id: int
    ) -> UserChatDTO:
        user = (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

        if not user:
            raise ValueError("User not found")

        messages = (
            db.query(Message)
            .filter(Message.user_id == user_id)
            .order_by(Message.created_at.asc())
            .all()
        )

        return UserChatDTO(
            user_id=user.id,
            name=user.name,
            phone_number=user.phone_number,
            email=user.email,
            messages=[
                MessageDTO(
                    message=msg.content,
                    sender=msg.sender,
                    time=str(msg.created_at)
                )
                for msg in messages
            ]
        )

