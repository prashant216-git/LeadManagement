from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    String,
    Text,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.models.base_model import BaseModel


class Tenant(BaseModel):
    """
    Represents a business/workspace using the CRM.
    """

    __tablename__ = "tenants"

    # ======================================================
    # BUSINESS IDENTITY
    # ======================================================

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    slug: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    # ======================================================
    # CONTACT INFORMATION
    # ======================================================

    email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    phone: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    # ======================================================
    # BUSINESS INFORMATION
    # ======================================================

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    website: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    # ======================================================
    # STATUS
    # ======================================================

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    # ======================================================
    # TRIAL
    # ======================================================

    is_trial: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    trial_ends_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # ======================================================
    # LOCALIZATION
    # ======================================================

    timezone: Mapped[str] = mapped_column(
        String(100),
        default="Asia/Kolkata",
        nullable=False,
    )

    currency: Mapped[str] = mapped_column(
        String(10),
        default="INR",
        nullable=False,
    )

    # ======================================================
    # RELATIONSHIPS
    # ======================================================

    channel_connections: Mapped[
        list["ChannelConnection"]
    ] = relationship(
        "ChannelConnection",
        back_populates="tenant",
    )