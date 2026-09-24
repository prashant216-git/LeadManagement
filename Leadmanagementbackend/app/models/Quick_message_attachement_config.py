from uuid import UUID

from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from enums.message import QuickMessageType
from models.base_model import BaseModel


class Quick_message_attachement_config(BaseModel):

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    Message_text: Mapped[Text] = mapped_column(
        Text,
        nullable=True,
    )

    Title: Mapped[Text] = mapped_column(
        Text,
        nullable=True,
    )
    attachment_url: Mapped[Text] = mapped_column(
        Text,
        nullable=True,
    )
    attachment_type: Mapped[Text] = mapped_column(
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
