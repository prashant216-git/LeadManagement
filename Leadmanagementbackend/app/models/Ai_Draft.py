from uuid import UUID

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import ForeignKey
from sqlalchemy import DateTime
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.sql import func

from app.db.database import Base


class AIDraft(Base):
    __tablename__ = "ai_drafts"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )

    message_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("messages.id"),
        nullable=False
    )

    draft_text = Column(
        Text,
        nullable=False
    )

    status = Column(
        String(50),
        default="generated"
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )