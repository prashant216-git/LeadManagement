import traceback
from uuid import UUID

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.DTOs.QuickMessageDTO import QuickMessageResponse, ListResponse
from app.enums.message import QuickMessageType
from app.models.Attachements import Attachment
from app.models.Quick_message_attachement_config import (
    Quick_message_attachement_config,
)
from app.repositories.AttachementRepository import AttachmentRepository
from app.repositories.QuickMessageRepository import QuickMessageRepository
from app.services.AttachementService import AttachmentService


class QuickMessageAttachmentService:

    def __init__(
        self,
        db,
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

            quick_message = self.repository.save(
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

                self.attachment_repository.save(
                    attachment_model
                )

            # Everything succeeded
            self.db.commit()


            return quick_message

        except Exception:

            print(traceback.format_exc())

            # Rollback database transaction
            self.db.rollback()

            # DB rollback cannot remove GCP object,
            # so remove it manually
            if uploaded_file:
                try:
                   print("rollbacked")
                except Exception:
                    # Log this properly in production
                    pass

            raise

    async def get_by_user_id(
            self,
            user_id: UUID,
    ) -> ListResponse:

        quick_messages = self.repository.get_all_by_user(user_id)
        print(len(quick_messages))

        items = []

        for message in quick_messages:

            attachment = self.attachment_repository.get_by_message(
                message.id
            )

            attachment_url = None

            if  attachment and attachment.temporary_url:
                attachment_url = attachment.temporary_url

            elif attachment:
                attachment_url = (
                    self.attachment_service.generate_signed_url(
                        attachment.file_path
                    )
                )
                attachment.temporary_url = attachment_url
                self.db.commit()


            items.append(
                QuickMessageResponse(
                    id=message.id,
                    message_text=message.Message_text,
                    title=message.Title,
                    attachment_type=message.attachment_type,
                    is_active=message.is_active,
                    attachment_url=attachment_url,
                )
            )

        return ListResponse(items=items)