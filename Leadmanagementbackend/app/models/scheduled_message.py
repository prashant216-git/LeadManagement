from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.enums.message import ScheduledMessageStatus
from app.models.base_model import BaseModel


class ScheduledMessage(BaseModel):
    __tablename__ = "scheduled_messages"



    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    lead_id: Mapped[UUID] = mapped_column(
        ForeignKey("leads.id"),
        nullable=False,
    )

    channel_connection_id: Mapped[UUID] = mapped_column(
        ForeignKey("channel_connections.id"),
        nullable=False,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    scheduled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        nullable=False,
        default=ScheduledMessageStatus.SCHEDULED,
    )

