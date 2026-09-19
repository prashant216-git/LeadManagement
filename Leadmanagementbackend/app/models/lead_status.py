from uuid import UUID

from sqlalchemy import ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base_model import BaseModel


class LeadStatus(BaseModel):
    __tablename__ = "lead_status"



    lead_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("leads.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    status_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("lead_status_master.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    update_by: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )

    __table_args__ = (
        Index(
            "uq_lead_status_lead",
            "lead_id",
            unique=True,
        ),
        Index(
            "idx_lead_status_status",
            "status_id",
        ),
    )

    lead = relationship(
        "Lead",
        back_populates="lead_statuses",
    )

    status = relationship(
        "LeadStatusMaster",
        back_populates="statuses",
    )
    updated_by_user = relationship(
        "User",
        foreign_keys=[update_by],
        back_populates="updated_lead_statuses",
    )