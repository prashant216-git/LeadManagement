from uuid import UUID

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base
from app.enums.message import AIDraftStatus
from app.models.base_model import BaseModel


class AIDraft(BaseModel):
    __tablename__ = "ai_drafts"

    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    lead_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("leads.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    message_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("messages.id", ondelete="CASCADE"),
        nullable=False,
        index=True,

    )

    draft_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=AIDraftStatus.GENERATED,
        index=True,
    )

    user = relationship(
        "User",
        back_populates="ai_drafts",
    )

    message = relationship(
        "Message",
        back_populates="ai_draft",
    )

    lead=relationship(
        "Lead",
        back_populates="ai_drafts",
    )