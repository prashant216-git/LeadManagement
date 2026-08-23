from datetime import datetime


from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    LargeBinary, UUID,
)

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.enums.channel import CredentialType
from app.models.base_model import BaseModel


class ChannelCredential(BaseModel):
    """
    Stores encrypted authentication credentials
    for a connected communication channel.
    """

    __tablename__ = "channel_credentials"

    __table_args__ = (
        Index(
            "idx_credential_connection",
            "channel_connection_id",
        ),
        Index(
            "idx_credential_expiry",
            "expires_at",
        ),
    )

    # --------------------------------------------------------
    # Relationship
    # --------------------------------------------------------

    channel_connection_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "channel_connections.id",
            ondelete="CASCADE",
        ),
        unique=True,
        nullable=False,
    )

    # --------------------------------------------------------
    # Credential Information
    # --------------------------------------------------------

    credential_type: Mapped[CredentialType] = mapped_column(
        Enum(CredentialType),
        nullable=False,
    )

    token_type: Mapped[str | None]

    expires_at: Mapped[datetime | None]

    last_refreshed_at: Mapped[datetime | None]

    # --------------------------------------------------------
    # Encryption
    # --------------------------------------------------------

    encrypted_payload: Mapped[bytes] = mapped_column(
        LargeBinary,
        nullable=False,
    )

    encryption_key_version: Mapped[int] = mapped_column(
        default=1,
        nullable=False,
    )

    credential_version: Mapped[int] = mapped_column(
        default=1,
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    # --------------------------------------------------------
    # Relationship
    # --------------------------------------------------------

    connection = relationship(
        "ChannelConnection",
        back_populates="credentials",
    )