from datetime import datetime

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Index,
    String,
    Text,
    JSON, UUID,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.models.base_model import BaseModel
from app.enums.message import (
    MessageDirection,
    MessageType,
)


class Message(BaseModel):
    """
    Represents a communication message associated with a lead.

    A message may come from any supported channel such as
    Gmail, WhatsApp, Telegram, or future providers.
    """

    __tablename__ = "messages"

    __table_args__ = (
        Index(
            "idx_message_lead",
            "lead_id",
        ),
        Index(
            "idx_message_connection",
            "channel_connection_id",
        ),
        Index(
            "idx_message_provider_id",
            "provider_message_id",
        ),
        Index(
            "idx_message_provider_created_at",
            "provider_created_at",
        ),
    )

    # ======================================================
    # LEAD MAPPING
    # ======================================================

    lead_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "leads.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    # ======================================================
    # CONVERSATION
    # ======================================================

    conversation_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # ======================================================
    # CHANNEL CONNECTION
    # ======================================================

    channel_connection_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "channel_connections.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    # ======================================================
    # PROVIDER IDENTITY
    # ======================================================

    provider_message_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # ======================================================
    # REPLY TO MESSAGE
    # ======================================================

    reply_to_message_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "messages.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )


    # ======================================================
    # MESSAGE DIRECTION
    # ======================================================

    direction: Mapped[MessageDirection | None] = mapped_column(
        Enum(MessageDirection),
        nullable=True,
    )
    rfc_message_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )


    # ======================================================
    # SENDER / RECIPIENT
    # ======================================================

    sender_identifier: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    recipient_identifier: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # ======================================================
    # CONTENT
    # ======================================================

    content: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    message_type: Mapped[MessageType | None] = mapped_column(
        Enum(MessageType),
        nullable=True,
    )

    # ======================================================
    # PROVIDER TIMESTAMP
    # ======================================================

    provider_created_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # ======================================================
    # RELATIONSHIPS
    # ======================================================

    lead = relationship(
        "Lead",
        back_populates="messages",
    )

    channel_connection = relationship(
        "ChannelConnection",
        back_populates="messages",
    )