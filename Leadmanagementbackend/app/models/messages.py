from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import ForeignKey
from sqlalchemy import DateTime
from sqlalchemy.sql import func

from app.db.database import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    channel = Column(
        String(50),
        nullable=False
    )

    channel_message_id = Column(
        String(255),
        unique=True,
        nullable=False
    )

    sender = Column(
        String(50),
        nullable=False
    )

    message_type = Column(
        String(50),
        nullable=False,
        default="text"
    )

    content = Column(
        Text,
        nullable=False
    )

    message_timestamp = Column(
        String(50),
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )