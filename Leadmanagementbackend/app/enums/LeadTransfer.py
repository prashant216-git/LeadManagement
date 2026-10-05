from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum as SQLEnum, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship




class LeadTransferType(str, Enum):
    SUMMARY = "SUMMARY"
    MESSAGES = "MESSAGES"
    BOTH = "BOTH"
    NONE = "NONE"


class LeadTransferStatus(str, Enum):
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    REVOKED = "REVOKED"


