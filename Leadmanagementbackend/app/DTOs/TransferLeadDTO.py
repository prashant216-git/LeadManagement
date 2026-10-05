from uuid import UUID

from pydantic import BaseModel

from app.enums.LeadTransfer import LeadTransferType


class TransferLeadRequest(BaseModel):
    lead_id: UUID
    transfer_to: UUID
    transfer_type: LeadTransferType
