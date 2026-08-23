from datetime import datetime

from sqlalchemy import (
    Boolean,
    Enum,
    ForeignKey,
    Index,
    String, UUID,
)
from sqlalchemy.dialects.postgresql import JSONB

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.enums.channel import WatchStatus
from app.models.base_model import BaseModel


class ChannelWatch(BaseModel):
    """
    Stores the state of an external provider's
    webhook/watch/subscription.

    Examples
    --------
    Gmail
        history_id
        expiration

    Outlook
        subscription_id
        expiration

    The model is provider-neutral.
    """

    __tablename__ = "channel_watches"

    __table_args__ = (
        Index(
            "idx_channel_watch_connection",
            "channel_connection_id",
        ),
        Index(
            "idx_channel_watch_expiration",
            "expires_at",
        ),
    )

    # ==========================================================
    # Connection
    # ==========================================================

    channel_connection_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "channel_connections.id",
            ondelete="CASCADE",
        ),
        unique=True,
        nullable=False,
    )

    # ==========================================================
    # Provider Watch Information
    # ==========================================================

    provider_subscription_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    provider_resource_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # Gmail historyId
    # Other providers can use their own resource/cursor ID.
    provider_cursor: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # ==========================================================
    # Watch Status
    # ==========================================================

    status: Mapped[WatchStatus] = mapped_column(
        Enum(WatchStatus),
        default=WatchStatus.ACTIVE,
        nullable=False,
    )

    # ==========================================================
    # Timing
    # ==========================================================

    started_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )

    expires_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )

    last_renewed_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )

    last_event_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )

    # ==========================================================
    # Provider Response / Metadata
    # ==========================================================

    provider_metadata: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    # ==========================================================
    # Active
    # ==========================================================

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    # ==========================================================
    # Relationship
    # ==========================================================

    connection = relationship(
        "ChannelConnection",
        back_populates="watch",
    )