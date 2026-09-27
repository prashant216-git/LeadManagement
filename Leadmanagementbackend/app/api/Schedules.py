from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.DTOs.MessageDTO import ScheduledMessageResponse, ScheduledMessageCreate, CancelledScheduledMessageResponse
from app.dependencies.services import (
    get_scheduled_message_service,
)
from app.services.ScheduledMessageservice import ScheduledMessageService

router = APIRouter(
    prefix="/schedules",
    tags=["Scheduled Messages"],
)


@router.post(
    "/schedule-message",
    response_model=ScheduledMessageResponse,
    status_code=status.HTTP_201_CREATED,
)
async def schedule_message(
    request: ScheduledMessageCreate,
    service: ScheduledMessageService = Depends(
        get_scheduled_message_service
    ),
):
    scheduled_message = await service.schedule_message(
        user_id=request.user_id,
        lead_id=request.lead_id,
        channel_connection_id=request.channel_connection_id,
        content=request.content,
        scheduled_at=request.scheduled_at,
    )

    return scheduled_message

@router.get(
    "/schedule-message/{lead_id}",

    response_model=list[ScheduledMessageResponse],
    status_code=status.HTTP_200_OK,
)
async def schedule_message(
    lead_id: UUID,
    service: ScheduledMessageService = Depends(
        get_scheduled_message_service
    ),
):
    result= await service.get_by_lead_id(lead_id=lead_id)
    return result


@router.post(
    "/schedule-message/cancel/{scheduled_message_id}",
    response_model=CancelledScheduledMessageResponse,
    
    status_code=status.HTTP_201_CREATED,
)
async def schedule_message(
scheduled_message_id: UUID,
    service: ScheduledMessageService = Depends(
        get_scheduled_message_service
    ),
):
    cancelled_message = await service.cancel_message(scheduled_message_id=scheduled_message_id)



    return CancelledScheduledMessageResponse(
        id=cancelled_message.id,
        content=cancelled_message.content,
        scheduled_at=cancelled_message.scheduled_at,
        cancelled_at=cancelled_message.updated_at,
        lead_id=cancelled_message.lead_id,
        channel_connection_id=cancelled_message.channel_connection_id,
        status=cancelled_message.status,
    )



