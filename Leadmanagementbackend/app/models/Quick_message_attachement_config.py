from uuid import UUID

from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.enums.message import QuickMessageType
from app.models.base_model import BaseModel


class Quick_message_attachement_config(BaseModel):

    __tablename__ = "quick_message_attachement_config"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    attachment_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("attachments.id"),
        nullable=True,
    )

    Message_text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    Title: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    attachment_type: Mapped[str | None] = mapped_column(
        nullable=True,
        default=QuickMessageType.TEXT
    )
    is_active: Mapped[bool] = mapped_column(
        nullable=False,
        default=True
    )
    created_by: Mapped[UUID] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )
    updated_by: Mapped[UUID] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )
