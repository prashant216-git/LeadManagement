from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.DTOs.MessageDTO import LeadMessagesResponseDTO
from app.db.session import get_db
from app.repositories.ChannelConnectionRepository import (
    ChannelConnectionRepository,
)
from app.repositories.LeadRepository import LeadRepository
from app.repositories.MessageRepository import MessageRepository
from app.services.Leadmanagementservice import LeadService
from app.services.messageservice import MessageService

router = APIRouter(
    prefix="/leads",
    tags=["Leads"],
)

def get_message_service(
    db: AsyncSession = Depends(get_db),
) -> MessageService:

    message_repository = MessageRepository(
        db
    )

    return MessageService(
        message_repository=message_repository
    )
def get_lead_service(
    db: AsyncSession = Depends(get_db),
) -> LeadService:

    lead_repository = LeadRepository(db)

    channel_connection_repository = (
        ChannelConnectionRepository(db)
    )

    return LeadService(
        lead_repository=lead_repository,
        channel_connection_repository=(
            channel_connection_repository
        ),
    )


@router.get(
    "/{channel_id}",
)
async def get_leads_by_channel(
    channel_id: int,

    page: int = Query(
        default=1,
        ge=1,
    ),

    page_size: int = Query(
        default=20,
        ge=1,
        le=100,
    ),

    sort_by: str = Query(
        default="created_at",
    ),

    sort_order: str = Query(
        default="desc",
        pattern="^(asc|desc)$",
    ),

    lead_service: LeadService = Depends(
        get_lead_service
    ),
):

    try:

        return await lead_service.get_lead_by_channel_id(
            channel_id=channel_id,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_order=sort_order,
        )

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except Exception as e:

        print(
            f"Failed to retrieve leads: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve leads.",
        )

@router.get(
    "/{lead_id}/messages",
    response_model=LeadMessagesResponseDTO,
)
async def get_lead_messages(
    lead_id: int,
    message_service: MessageService = Depends(
        get_message_service
    ),
):

    try:

        return await message_service.get_messages_by_lead_id(
            lead_id=lead_id,
        )

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except Exception as e:

        print(
            f"Failed to retrieve lead messages: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve lead messages.",
        )