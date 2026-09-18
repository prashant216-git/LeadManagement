from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base_model import BaseModel


class LeadStatusMaster(BaseModel):
    __tablename__ = "lead_status_master"

    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    status_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    is_default: Mapped[str] = mapped_column(
        Boolean,
        default=False
        ,


    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    created_by: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    user = relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="lead_statuses",
    )

    created_by_user = relationship(
        "User",
        foreign_keys=[created_by],
        back_populates="created_lead_statuses",
    )

    statuses: Mapped[list["LeadStatus"]] = relationship(
        "LeadStatus",
        back_populates="status",
        cascade="all, delete-orphan",
    )