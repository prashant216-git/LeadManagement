from __future__ import annotations

from uuid import UUID

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.Users import User
from app.models.messages import Message

from app.models.base_model import BaseModel


class Lead(BaseModel):
    __tablename__ = "leads"

    # ======================================================
    # User
    # ======================================================

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    # ======================================================
    # Lead Information
    # ======================================================

    name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    phone_number: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    # ======================================================
    # AI / CRM
    # ======================================================

    summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    source_channel_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(
            "channel_master.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    channel_connection_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(
            "channel_connections.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    # ======================================================
    # Relationships
    # ======================================================

    user: Mapped["User"] = relationship("User", back_populates="leads")

    messages: Mapped[list["Message"]] = relationship(
        "Message",
        back_populates="lead",
    )
    ai_drafts: Mapped[list["AIDraft"]] = relationship(
        "AIDraft",
        back_populates="lead",
        cascade="all, delete-orphan",
    )