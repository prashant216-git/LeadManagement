from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    Enum,
    ForeignKey,
    Index,
    String,
    Uuid,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.enums.channel import (
    AdminStatus,
    ConnectionStatus,
)
from app.models.base_model import BaseModel

if TYPE_CHECKING:
    from app.models.channel_credential import ChannelCredential
    from app.models.channel_master import ChannelMaster
    from app.models.ChannelWatch import ChannelWatch
    from app.models.messages import Message
    from app.models.Users import User


class ChannelConnection(BaseModel):
    __tablename__ = "channel_connections"

    __table_args__ = (
        Index(
            "uq_active_channel_connection",
            "user_id",
            "channel_id",
            "provider_account_id",
            unique=True,
            postgresql_where=text("connection_status = 'CONNECTED'"),
        ),
        Index("idx_channel_user", "user_id"),
        Index("idx_channel_provider", "provider_account_id"),
    )

    # ==========================================================
    # Ownership
    # ==========================================================

    user_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    channel_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("channel_master.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    created_by: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id"),
        nullable=False,
    )

    # ==========================================================
    # Provider Identity
    # ==========================================================

    provider_account_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    provider_identifier: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    display_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # ==========================================================
    # Status
    # ==========================================================

    connection_status: Mapped[ConnectionStatus] = mapped_column(
        Enum(ConnectionStatus),
        default=ConnectionStatus.CONNECTING,
        nullable=False,
    )

    admin_status: Mapped[AdminStatus] = mapped_column(
        Enum(AdminStatus),
        default=AdminStatus.ACTIVE,
        nullable=False,
    )

    # ==========================================================
    # Monitoring
    # ==========================================================

    connected_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )

    disconnected_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )

    last_sync_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )

    last_health_check_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )
    provider_metadata: Mapped[dict | None] = mapped_column(
        "metadata",
        JSONB,
        nullable=True,
        default=dict,
    )

    connection_reference: Mapped[str | None] = mapped_column(
        String(2000),
        nullable=True,
    )


    oauth_state: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        unique=True,
        index=True,
    )

    # ==========================================================
    # Relationships
    # ==========================================================

    user: Mapped["User"] = relationship(
        "User",
        back_populates="channel_connections",
        foreign_keys=[user_id],
    )

    creator: Mapped["User"] = relationship(
        "User",
        foreign_keys=[created_by],
    )

    channel: Mapped["ChannelMaster"] = relationship(
        "ChannelMaster",
        back_populates="connections",
    )

    credentials: Mapped["ChannelCredential | None"] = relationship(
        "ChannelCredential",
        back_populates="connection",
        uselist=False,
        cascade="all, delete-orphan",
    )

    watch: Mapped["ChannelWatch | None"] = relationship(
        "ChannelWatch",
        back_populates="connection",
        uselist=False,
        cascade="all, delete-orphan",
    )

    messages: Mapped[list["Message"]] = relationship(
        "Message",
        back_populates="channel_connection",
    )