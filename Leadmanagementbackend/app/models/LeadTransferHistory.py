from uuid import UUID

from sqlalchemy import ForeignKey, Text, Column
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base_model import BaseModel
from app.enums.LeadTransfer import (
    LeadTransferType,
    LeadTransferStatus,
)


class LeadTransferHistory(BaseModel):
    __tablename__ = "lead_transfer_history"

    # ==================================================
    # Lead
    # ==================================================

    lead_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey(
            "leads.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    # ==================================================
    # Transfer Users
    # ==================================================

    transfer_from: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    transfer_to: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    # ==================================================
    # Transfer Information
    # ==================================================

    transfer_type: Mapped[LeadTransferType] = mapped_column(
        SQLEnum(
            LeadTransferType,
            name="lead_transfer_type",
        ),
        nullable=False,
    )

    transfer_status: Mapped[LeadTransferStatus] = mapped_column(
        SQLEnum(
            LeadTransferStatus,
            name="lead_transfer_status",
        ),
        nullable=False,
        default=LeadTransferStatus.COMPLETED,
    )

    comment = Column(Text, nullable=True)

    # ==================================================
    # Source Channel
    # ==================================================


    # ==================================================
    # Audit
    # ==================================================

    created_by: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    updated_by: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )