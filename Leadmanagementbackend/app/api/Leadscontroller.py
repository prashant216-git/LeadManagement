from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.DTOs.ChannelLeadidentifier import LeadChannelIdentifiersDTO
from app.DTOs.Chats import ChatSidebarDTO
from app.DTOs.CreateManualLeadDTO import CreateManualLeadDTO
from app.DTOs.MessageDTO import LeadMessagesResponseDTO
from app.db.session import get_db
from app.repositories.ChannelConnectionRepository import (
    ChannelConnectionRepository,
)
from app.repositories.LeadRepository import LeadRepository
from app.repositories.MessageRepository import MessageRepository
from app.services.Chatservice import ChatService
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
        message_repository=message_repository,lead_repository=LeadRepository(db)
    )

def get_chat_service(
    db: AsyncSession = Depends(get_db),
) -> ChatService:

    return ChatService(
        lead_repository=LeadRepository(db),
        message_repository=MessageRepository(db),
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
    "/all",
)
async def get_leads(
    channel_id: UUID | None = Query(
        default=None,
    ),

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
        get_lead_service,
    ),
):

    try:

        if channel_id is None:

            return await (
                lead_service
                .get_manual_leads(
                    page=page,
                    page_size=page_size,
                    sort_by=sort_by,
                    sort_order=sort_order,
                )
            )

        return await (
            lead_service
            .get_lead_by_channel_id(
                channel_id=channel_id,
                page=page,
                page_size=page_size,
                sort_by=sort_by,
                sort_order=sort_order,
            )
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
    "/{lead_id}/messages/{channel_id}",
    response_model=LeadMessagesResponseDTO,
)
async def get_lead_messages(
    lead_id: UUID,
    channel_id:UUID,

    message_service: MessageService = Depends(
        get_message_service
    ),
):

    try:

        return await message_service.get_messages_by_lead_id(
            lead_id=lead_id,channel_id=channel_id
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
@router.post(
    "/create_manual_lead",
    status_code=status.HTTP_201_CREATED,
)
async def create_lead_manual(
    lead_details: CreateManualLeadDTO = Body(
        ...,

    ),
    lead_service=Depends(
        get_lead_service,
    ),
):

    try:

        user_id = UUID("9ad69636-f013-49f6-9cce-00f2828dbc6f")

        created_lead = (
            await lead_service.create_manual_lead(
                user_id=user_id,
                lead_data=lead_details,
            )
        )

        return created_lead

    except ValueError as e:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

@router.get(
    "/{lead_id}/channels/{channel_id}/identifiers",
    response_model=LeadChannelIdentifiersDTO,
)
async def get_lead_channel_identifiers(
    lead_id: UUID,
    channel_id: UUID,
    lead_service: LeadService = Depends(
        get_lead_service
    ),
):

    try:

        return await lead_service.get_lead_channel_identifiers(
            lead_id=lead_id,
            channel_id=channel_id,
        )

    except ValueError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e),
        )

    except Exception as e:

        print(
            f"Failed to retrieve channel identifiers: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve channel identifiers.",
        )


@router.get(
    "/sidebar/{channel_id}",
    response_model=ChatSidebarDTO,
)
async def get_chat_sidebar(
    channel_id: UUID,
    chat_service: ChatService = Depends(
        get_chat_service
    ),
):

    return await chat_service.get_chat_sidebar(
        channel_id=channel_id
    )

