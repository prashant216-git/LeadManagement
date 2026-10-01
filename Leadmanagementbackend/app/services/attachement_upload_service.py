import traceback
from uuid import UUID

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.Attachements import Attachment
from app.repositories.AttachementRepository import AttachmentRepository
from app.services.AttachementService import AttachmentService


class AttachmentUploadService:

    def __init__(
        self,
        db: AsyncSession,
        attachment_repository: AttachmentRepository,
        attachment_service: AttachmentService,
    ):
        self.db = db
        self.attachment_repository = attachment_repository
        self.attachment_service = attachment_service

    async def upload(
            self,
            user_id: UUID,
            attachments: list[UploadFile],
            message_id: UUID | None = None,
            lead_id: UUID | None = None,
    ) -> list[UUID]:

        uploaded_files = []
        attachment_ids = []

        try:
            for attachment in attachments:
                # Upload file to GCS
                uploaded_file = await self.attachment_service.upload(
                    file=attachment,
                    user_id=user_id,
                    message_id=message_id,
                )

                uploaded_files.append(uploaded_file)

                # Save attachment details in DB
                attachment_model = Attachment(
                    user_id=user_id,
                    message_id=message_id,
                    lead_id=lead_id,
                    file_name=uploaded_file["file_name"],
                    file_path=uploaded_file["file_path"],
                    file_type=uploaded_file["file_type"],
                    file_size=uploaded_file["file_size"],
                )

                attachment_model = self.attachment_repository.save(
                    attachment_model
                )

                attachment_ids.append(attachment_model.id)

            # Commit all attachment records together
            self.db.commit()

            return attachment_ids

        except Exception:
            print(traceback.format_exc())

            self.db.rollback()

            # DB rollback does not remove GCS files
            for uploaded_file in uploaded_files:
                try:
                    await self.attachment_service.delete(
                        uploaded_file["file_path"]
                    )
                except Exception:
                    print(
                        f"Failed to delete GCS file: "
                        f"{uploaded_file['file_path']}"
                    )

            raise