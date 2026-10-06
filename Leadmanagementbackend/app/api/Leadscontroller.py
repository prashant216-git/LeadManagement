from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.DTOs.TransferLeadDTO import TransferLeadRequest
from app.DTOs.Leadlist import Leadetails
from app.DTOs.ChannelLeadidentifier import LeadChannelIdentifiersDTO
from app.DTOs.Chats import ChatSidebarDTO
from app.DTOs.CreateManualLeadDTO import CreateManualLeadDTO
from app.DTOs.MessageDTO import LeadMessagesResponseDTO

from app.dependencies.services import get_lead_service, get_message_service, get_chat_service

from app.services.Chatservice import ChatService
from app.services.Leadmanagementservice import LeadService
from app.services.messageservice import MessageService
from app.enums.LeadTransfer import LeadTransferType, LeadTransferStatus

router = APIRouter(
    prefix="/leads",
    tags=["Leads"],
)




@router.get(
    "/all",
)
async def get_leads(
    channel_id: UUID | None = Query(
        default=None,
    ),

    transfer_type: str | None = Query(
        default=None,
        pattern="^(TRANSFER_IN|TRANSFER_OUT)$",
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
        user_id = UUID(
            "09a81c46-92c4-42ae-9ffe-4275d62f1d9f"
        )

        # ---------------------------------------------
        # TRANSFER IN / OUT
        # ---------------------------------------------

        if transfer_type is not None:

            return await lead_service.get_transfer_history(
                channel_id=channel_id,
                transfer_type=transfer_type,
                page=page,
                page_size=page_size,
                sort_by=sort_by,
                sort_order=sort_order,
                user_id=user_id
            )

        # ---------------------------------------------
        # NORMAL LEADS
        # ---------------------------------------------

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
    response_model=Leadetails,
    status_code=status.HTTP_201_CREATED,
)
async def create_lead_manual(
    lead_details: CreateManualLeadDTO = Body(...),
    lead_service=Depends(get_lead_service),
):
    try:

        user_id = UUID(
            "09a81c46-92c4-42ae-9ffe-4275d62f1d9f"
        )

        return await lead_service.create_manual_lead(
            user_id=user_id,
            lead_data=lead_details,
        )

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
    user_id=UUID("09a81c46-92c4-42ae-9ffe-4275d62f1d9f")

    return await chat_service.get_chat_sidebar(
        channel_id=channel_id,user_id=user_id
    )

@router.get(
    "/transfer/types"
)
async def get_transfer_enums():

    return {
        "transfer_types": [
            {
                "key": transfer_type.name,
                "value": transfer_type.value,
            }
            for transfer_type in LeadTransferType
        ],

    }

@router.post(
    "/transfer",
    status_code=status.HTTP_200_OK,
)
async def transfer_lead(
    request: TransferLeadRequest,
    lead_service: LeadService = Depends(
        get_lead_service
    ),
):
    try:

        # Replace this with current_user.user_id
        # once your JWT dependency is connected.
        current_user_id = UUID(
            "09a81c46-92c4-42ae-9ffe-4275d62f1d9f"
        )

        lead = await lead_service.transfer_lead(
            lead_id=request.lead_id,
            transfer_to=request.transfer_to,
            transfer_type=request.transfer_type,
            comment=request.comment,

            current_user_id=current_user_id,
        )

        return {
            "message": "Lead transferred successfully.",
            "lead_id": lead.id,
            "assigned_user_id": lead.assigned_user_id,
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except Exception as e:
        print(e)
        raise HTTPException(

            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to transfer lead.",
        )


