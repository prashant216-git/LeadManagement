from __future__ import annotations

from datetime import datetime
from uuid import UUID



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



class User(BaseModel):




    __tablename__ = "users"

    # Identity

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    password: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    # Status

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    # Audit

    created_by: Mapped[UUID | None]

    channel_connections: Mapped[list["ChannelConnection"]] = relationship(
        "ChannelConnection",
        back_populates="user",  # ✅ Match singular name on ChannelConnection
        foreign_keys="ChannelConnection.user_id",  # ✅ Disambiguates user_id from created_by
    )
    leads: Mapped[list["Lead"]] = relationship(
        "Lead",
        back_populates="user",  # ✅ Match singular name on Lead
        cascade="all, delete-orphan",
    )
    ai_drafts: Mapped[list["AIDraft"]] = relationship(
        "AIDraft",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    lead_statuses: Mapped[list["LeadStatusMaster"]] = relationship(
        "LeadStatusMaster",
        foreign_keys="LeadStatusMaster.user_id",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    created_lead_statuses: Mapped[list["LeadStatusMaster"]] = relationship(
        "LeadStatusMaster",
        foreign_keys="LeadStatusMaster.created_by",
        back_populates="created_by_user",
    )