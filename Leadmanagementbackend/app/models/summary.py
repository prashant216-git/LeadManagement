from sqlalchemy import ForeignKey, Integer, Text, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Summary(Base):

    __tablename__ = "summaries"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    lead_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "leads.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        unique=True,
        index=True,
    )

    summary_user: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    summary_sales: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    last_summarized_message_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "messages.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    lead: Mapped["Lead"] = relationship(
        "Lead",
        back_populates="summary",
    )

    last_summarized_message: Mapped["Message | None"] = relationship(
        "Message",
        foreign_keys=[last_summarized_message_id],
    )