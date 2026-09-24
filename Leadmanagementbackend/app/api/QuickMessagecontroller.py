from fastapi import APIRouter, Form, UploadFile, File, Depends
from uuid import UUID

from dependencies.services import get_quick_message_service
from enums.message import QuickMessageType
from services.QuickMessageService import QuickMessageAttachmentService

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

@router.post("/create")
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

        return {
            "message": "Quick message created successfully",
            "data": quick_message,
        }

    except Exception as e:
        raise e