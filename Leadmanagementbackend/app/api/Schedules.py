from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.DTOs.MessageDTO import ScheduledMessageResponse, ScheduledMessageCreate
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