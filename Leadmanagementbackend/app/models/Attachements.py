from uuid import UUID

from sqlalchemy import Text
from sqlalchemy.orm import Mapped, mapped_column

from models.base_model import BaseModel


class Attachment(BaseModel):

    __tablename__ = "attachments"

    user_id: Mapped[UUID] = mapped_column(
        nullable=False,
    )

    lead_id: Mapped[UUID | None] = mapped_column(
        nullable=True,
    )

    message_id: Mapped[UUID | None] = mapped_column(
        nullable=True,
    )

    file_name: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    file_path: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    file_type: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    file_size: Mapped[int] = mapped_column(
        nullable=False,
    )

