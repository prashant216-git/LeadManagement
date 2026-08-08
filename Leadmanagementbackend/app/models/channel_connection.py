from datetime import datetime

from sqlalchemy import (
    Enum,
    ForeignKey,
    Index,
    String,
    UniqueConstraint,
)
from app.models.tenant import Tenant
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.enums.channel import (
    AdminStatus,
    ConnectionStatus,
)

from app.models.base_model import BaseModel


class ChannelConnection(BaseModel):
    """
    Represents a connected communication account.

    The record is created when a user starts connecting
    a channel and may initially exist in CONNECTING state.

    Example lifecycle:

        CONNECTING
            ↓
        CONNECTED
            ↓
        DISCONNECTED
    """

    __tablename__ = "channel_connections"

    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "channel_id",
            "provider_account_id",
            name="uq_channel_connection",
        ),

        Index(
            "idx_channel_tenant",
            "tenant_id",
        ),

        Index(
            "idx_channel_provider",
            "provider_account_id",
        ),
    )

    # ==========================================================
    # Ownership
    # ==========================================================

    tenant_id: Mapped[int] = mapped_column(
        ForeignKey("tenants.id"),
        nullable=False,
    )

    channel_id: Mapped[int] = mapped_column(
        ForeignKey("channel_master.id"),
        nullable=False,
    )

    created_by: Mapped[int] = mapped_column(

        nullable=False,
    )

    # ==========================================================
    # Provider Identity
    # ==========================================================

    # Unknown until OAuth/provider authorization completes.
    provider_account_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # Provider-specific identifier.
    # Example:
    # Gmail -> email address
    # WhatsApp -> phone number/account identifier
    provider_identifier: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # Friendly name shown in the CRM.
    # Unknown during initial connection.
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
    connection_url: Mapped[str | None] = mapped_column(
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

    channel = relationship(
        "ChannelMaster",
        back_populates="connections",
    )

    credentials = relationship(
        "ChannelCredential",
        back_populates="connection",
        uselist=False,
        cascade="all, delete-orphan",
    )
    tenant: Mapped["Tenant"] = relationship(
        "Tenant",
        back_populates="channel_connections",
    )