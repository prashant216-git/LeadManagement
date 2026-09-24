from uuid import UUID

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from enums.message import QuickMessageType
from models.Attachements import Attachment
from models.Quick_message_attachement_config import (
    Quick_message_attachement_config,
)
from repositories.AttachementRepository import AttachmentRepository
from repositories.QuickMessageRepository import QuickMessageRepository
from services.AttachementService import AttachmentService


class QuickMessageAttachmentService:

    def __init__(
        self,
        db: AsyncSession,
        repository: QuickMessageRepository,
        attachment_repository: AttachmentRepository,
        attachment_service: AttachmentService,
    ):
        self.db = db
        self.repository = repository
        self.attachment_repository = attachment_repository
        self.attachment_service = attachment_service

    async def create(
        self,
        user_id: UUID,
        message_text: str | None,
        title: str | None,
        attachment_type: QuickMessageType,
        attachment: UploadFile | None,
    ):

        uploaded_file = None

        try:

            # Create quick message
            quick_message = Quick_message_attachement_config(
                user_id=user_id,
                Message_text=message_text,
                Title=title,
                attachment_type=attachment_type,
                is_active=True,
                created_by=user_id,
                updated_by=user_id,
            )

            quick_message = await self.repository.save(
                quick_message
            )

            # If attachment exists
            if attachment:

                uploaded_file = (
                    await self.attachment_service.upload(
                        file=attachment,
                        user_id=user_id,
                        message_id=quick_message.id,
                    )
                )

                attachment_model = Attachment(
                    user_id=user_id,
                    message_id=quick_message.id,
                    file_name=uploaded_file["file_name"],
                    file_path=uploaded_file["file_path"],
                    file_type=uploaded_file["file_type"],
                    file_size=uploaded_file["file_size"],
                )

                await self.attachment_repository.save(
                    attachment_model
                )

            # Everything succeeded
            await self.db.commit()

            return quick_message

        except Exception:

            # Rollback database transaction
            await self.db.rollback()

            # DB rollback cannot remove GCP object,
            # so remove it manually
            if uploaded_file:
                try:
                   print("rollbacked")
                except Exception:
                    # Log this properly in production
                    pass

            raise