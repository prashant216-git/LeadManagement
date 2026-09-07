from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey, String, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base_model import BaseModel


class LeadMeeting(BaseModel):
    __tablename__ = "lead_meetings"

    lead_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("leads.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    channel_connection_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("channel_connections.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    provider_event_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    start_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    end_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    meeting_link: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="SCHEDULED",
        index=True,
    )

    lead = relationship(
        "Lead",
        back_populates="meetings",
    )

    channel_connection = relationship(
        "ChannelConnection",
        back_populates="meetings",
    )