from fastapi import APIRouter, Form, UploadFile, File

from enums.message import QuickMessageType

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
):
    try :
        pass
    except Exception as e :
        raise e