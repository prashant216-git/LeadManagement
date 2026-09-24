from fastapi import APIRouter, Form, UploadFile, File, Depends
from uuid import UUID

from starlette import status

from app.DTOs.QuickMessageDTO import ListResponse
from app.dependencies.services import get_quick_message_service
from app.enums.message import QuickMessageType
from app.services.QuickMessageService import QuickMessageAttachmentService

router =APIRouter(prefix="/quick_meesage", tags=["Quick Messages"])

@router.get("types")
async def get_quick_message_types():
    return [
        {
            "value": item.value,
            "label": item.name,
        }
        for item in QuickMessageType
    ]

@router.post("/create",status_code=status.HTTP_201_CREATED)
async def create_quick_message(
    message_text: str | None = Form(None),
    title: str | None = Form(None),
    attachment_type: QuickMessageType = Form(QuickMessageType.TEXT),
    attachment: UploadFile | None = File(None),



    service: QuickMessageAttachmentService = Depends(
        get_quick_message_service
    ),
):
    try:

        user_id=UUID("09a81c46-92c4-42ae-9ffe-4275d62f1d9f")
        quick_message = await service.create(
            user_id=user_id,
            message_text=message_text,
            title=title,
            attachment_type=attachment_type,
            attachment=attachment,
        )
        print(quick_message)

        return {
            "message": "Quick message created successfully",
            "data": quick_message.id,
        }

    except Exception as e:
        raise e

@router.get("/user", response_model=ListResponse)
async def get_quick_messages_by_user(

    service: QuickMessageAttachmentService = Depends(
        get_quick_message_service
    ),
):
    user_id: UUID = UUID("09a81c46-92c4-42ae-9ffe-4275d62f1d9f")
    return await service.get_by_user_id(user_id)