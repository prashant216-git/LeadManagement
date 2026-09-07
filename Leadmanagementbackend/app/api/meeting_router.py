from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.DTOs.MeetingDTO import (
    CreateMeetingDTO,
    MeetingResponseDTO,
)
from app.services.MeetingService import MeetingService
from app.dependencies.meetingservice import get_meeting_service


router = APIRouter(
    prefix="/meetings",
    tags=["Meetings"],
)


@router.post(
    "/create",
    response_model=MeetingResponseDTO,
)
async def create_meeting(
    request: CreateMeetingDTO,
    meeting_service: MeetingService = Depends(
        get_meeting_service
    ),
):
    try:
        meeting = await meeting_service.create_meeting(
            lead_id=request.lead_id,
            channel_connection_id=request.channel_connection_id,
            title=request.title,
            description=request.description,
            start_time=request.start_time,
            end_time=request.end_time,
        )

        return meeting

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )
@router.get(
    "/{lead_id}}",
    response_model=MeetingResponseDTO,
)
async def get_meetings_by_lead(
    lead_id: UUID,
    meeting_service: MeetingService = Depends(
        get_meeting_service
    ),
):
    try:
        return meeting_service.get_meetings_by_lead_id(
            lead_id=lead_id
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )