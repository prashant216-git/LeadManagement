from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.db.database import Base


class Lead(Base):
    __tablename__ = "leads"

    # ======================================================
    # Primary Key
    # ======================================================

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )



    # ======================================================
    # Tenant
    # ======================================================

    tenant_id = Column(
        Integer,
        ForeignKey(
            "tenants.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    # ======================================================
    # Lead Information
    # ======================================================

    name = Column(
        String(255),
        nullable=True,
    )

    email = Column(
        String(255),
        nullable=True,
    )

    phone_number = Column(
        String(20),
        nullable=True,
    )

    # ======================================================
    # AI / CRM
    # ======================================================

    summary = Column(
        String,
        nullable=True,
    )

    source_channel_id = Column(
        Integer,
        ForeignKey(
            "channel_master.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )



    # ======================================================
    # Timestamps
    # ======================================================

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    # ======================================================
    # Relationships
    # ======================================================

    tenant = relationship(
        "Tenant",
        back_populates="leads",
    )
    messages = relationship(
        "Message",
        back_populates="lead",
    )