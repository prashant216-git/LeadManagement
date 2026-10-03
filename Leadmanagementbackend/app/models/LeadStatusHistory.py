from sqlalchemy import Column, ForeignKey, DateTime, func, Text

from app.models.base_model import BaseModel


class LeadStatusHistory(BaseModel):
    __tablename__ = "lead_status_history"



    lead_id = Column(
        ForeignKey("leads.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    status_id = Column(
        ForeignKey("lead_status_master.id"),
        nullable=False,
    )

    comment = Column(Text, nullable=True)

    changed_by = Column(
        ForeignKey("users.id"),
        nullable=True,
    )

    

