from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from app.DTOs.LeadStatusHistoryResponse import LeadStatusHistoryResponse
from app.DTOs.LeadStatusDTO import (
    LeadStatusCreateDTO,
    LeadStatusResponseDTO,
    LeadStatusUpdateDTO, ChangeLeadStatusDTO,
)
from app.services.LeadStatusService import LeadStatusService
from app.dependencies.services import get_lead_status_service, get_lead_service

router = APIRouter(
    prefix="/lead-status",
    tags=["Lead Status"],
)




@router.get(
    "/user",
    response_model=list[LeadStatusResponseDTO],
)
async def get_user_statuses(

    service: LeadStatusService = Depends(
        get_lead_status_service
    ),
):
    try:
        user_id=UUID("09a81c46-92c4-42ae-9ffe-4275d62f1d9f")
        return await service.get_statuses_by_user(
            user_id=user_id
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

@router.post(
    "",
    response_model=LeadStatusResponseDTO,
)
async def create_status(
    request: LeadStatusCreateDTO,

    service: LeadStatusService = Depends(
        get_lead_status_service
    ),
):
    try:
        user_id = UUID("09a81c46-92c4-42ae-9ffe-4275d62f1d9f")
        return await service.create_status(
            user_id=user_id,
            status_name=request.status_name,
            is_active=request.is_active,
            is_default=request.is_default,
            colour=request.colour,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

@router.patch(
    "/{status_id}",
    response_model=LeadStatusResponseDTO,
)
async def edit_status(
    status_id: UUID,
    request: LeadStatusUpdateDTO,

    service: LeadStatusService = Depends(
        get_lead_status_service
    ),
):
    try:
        user_id = UUID("09a81c46-92c4-42ae-9ffe-4275d62f1d9f")
        return await service.edit_status(
            user_id=user_id,
            status_id=status_id,
            status_name=request.status_name,
            is_active=request.is_active,
            is_default=request.is_default,
            colour=request.colour,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

@router.delete(
    "/{status_id}",
)
async def delete_status(
    status_id: UUID,

    service: LeadStatusService = Depends(
        get_lead_status_service
    ),
):
    try:
        user_id = UUID("09a81c46-92c4-42ae-9ffe-4275d62f1d9f")
        await service.delete_status(
            user_id=user_id,
            status_id=status_id,
        )

        return {
            "message": "Lead status deleted successfully."
        }

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


@router.post(
    "/change",
)
async def change_status(
    request: ChangeLeadStatusDTO,

    service: LeadStatusService = Depends(
        get_lead_status_service
    ),
):
    try:
        user_id = UUID("09a81c46-92c4-42ae-9ffe-4275d62f1d9f")


        if request.lead_id is None:
            raise ValueError(
                "Lead ID is required."
            )

        if request.status_id is None:
            raise ValueError(
                "Status ID is required."
            )

        lead_status = await service.change_status(
            user_id=user_id,
            lead_id=request.lead_id,
            status_id=request.status_id,
            comment=request.comment,
        )

        return lead_status

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

@router.get(
    "/{lead_id}/history",
    response_model=list[LeadStatusHistoryResponse],
    status_code=status.HTTP_200_OK,
)
async def get_lead_history(
    lead_id: UUID,
    lead_status_service=Depends(get_lead_status_service),
):
    try:
        return await lead_status_service.get_status_history(
            lead_id=lead_id
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )