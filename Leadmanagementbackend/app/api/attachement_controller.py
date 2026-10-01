from uuid import UUID
from typing import List
from fastapi import APIRouter, UploadFile, File, Depends

from app.dependencies.services import get_attachment_upload_service
from app.services import attachement_upload_service
from app.services.attachement_upload_service import AttachmentUploadService

router = APIRouter(
    prefix="/attahcement",
    tags=["attahcement"],

)

@router.post("/attachments")
async def upload_attachments(
    files: List[UploadFile] = File(...),
    attachment_upload_service: AttachmentUploadService = Depends(
        get_attachment_upload_service
    ),
):
    user_id = UUID("09a81c46-92c4-42ae-9ffe-4275d62f1d9f")

    return await attachment_upload_service.upload(
        user_id=user_id,
        attachments=files,
    )