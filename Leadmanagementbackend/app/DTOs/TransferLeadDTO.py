from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.enums.LeadTransfer import LeadTransferType, LeadTransferStatus


class TransferLeadRequest(BaseModel):
    lead_id: UUID
    transfer_to: UUID
    transfer_type: LeadTransferType
    comment: str

class TransferLeadResponseDTO(BaseModel):
    # ---------------------------------------------
    # Lead
    # ---------------------------------------------

    id: UUID



    assigned_user_id: UUID | None = None

    name: str | None = None

    email: str | None = None

    phone_number: str | None = None

    source_channel_id: UUID | None = None
    transfer_comment : str | None = None
    lead_status: UUID | None = None



    created_at: datetime

    updated_at: datetime

    # ---------------------------------------------
    # Transfer
    # ---------------------------------------------

    transfer_id: UUID

    transfer_from: UUID

    transfer_to: UUID

    transfer_type: LeadTransferType

    transfer_status: LeadTransferStatus

    comment: str | None= None

    transfer_created_at: datetime

    transfer_updated_at: datetime | None = None


class TransferLeadListResponseDTO(BaseModel):
    items: list[TransferLeadResponseDTO]

    page: int

    page_size: int

    total: int

    total_pages: int
