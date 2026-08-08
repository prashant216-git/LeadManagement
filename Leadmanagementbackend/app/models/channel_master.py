from sqlalchemy import (
    Boolean,
    Enum,
    String,
    Text,
)

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.enums.channel import (
    AuthType,
    ChannelCategory,
    ChannelStatus,
)
from app.models.base_model import BaseModel


class ChannelMaster(BaseModel):
    """
    Master table containing all supported communication providers.
    Example:
        - WhatsApp
        - Gmail
        - Outlook
        - Telegram
    """

    __tablename__ = "channel_master"

    code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    category: Mapped[ChannelCategory] = mapped_column(
        Enum(ChannelCategory),
        nullable=False,
    )

    auth_type: Mapped[AuthType] = mapped_column(
        Enum(AuthType),
        nullable=False,
    )

    status: Mapped[ChannelStatus] = mapped_column(
        Enum(ChannelStatus),
        default=ChannelStatus.ACTIVE,
        nullable=False,
    )

    supports_send: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    supports_receive: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    supports_webhook: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    supports_oauth: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    supports_media: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    supports_sync: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    icon: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    connections = relationship(
        "ChannelConnection",
        back_populates="channel",
    )