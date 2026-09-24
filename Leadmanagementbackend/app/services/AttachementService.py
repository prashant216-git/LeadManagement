import asyncio
from datetime import timedelta
from pathlib import Path
from uuid import UUID, uuid4
from google.oauth2 import service_account
from fastapi import UploadFile
from google.cloud import storage
from functools import partial

from app.core.config import settings


class AttachmentService:

    MAX_FILE_SIZE = 10 * 1024 * 1024

    ALLOWED_CONTENT_TYPES = {
        "application/pdf",
        "image/jpeg",
        "image/png",
    }

    def __init__(self):
        private_key = settings.GCP_PRIVATE_KEY.replace("\\n", "\n")

        print(repr(private_key[:80]))
        print(repr(private_key[-50:]))
        credentials = service_account.Credentials.from_service_account_info(
            {
                "type": "service_account",
                "project_id": settings.GCP_PROJECT_ID,
                "private_key_id": settings.GCP_PRIVATE_KEY_ID,
                "private_key": settings.GCP_PRIVATE_KEY.replace("\\n", "\n"),
                "client_email": settings.GCP_CLIENT_EMAIL,
                "client_id": settings.GCP_CLIENT_ID,
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        )
        self.client = storage.Client(
            project=settings.GCP_PROJECT_ID,
            credentials=credentials,
        )

        self.bucket = self.client.bucket(
            settings.GCP_BUCKET_NAME
        )

    async def upload(
        self,
        file: UploadFile,
        user_id: str | UUID,
        lead_id: UUID | None = None,
        message_id: UUID | None = None,
    ) -> dict:

        if file.content_type not in self.ALLOWED_CONTENT_TYPES:
            raise ValueError(
                f"File type {file.content_type} is not supported"
            )

        if file.size and file.size > self.MAX_FILE_SIZE:
            raise ValueError(
                "File size must be less than 10 MB"
            )

        extension = Path(file.filename or "").suffix.lower()
        file_name = f"{uuid4()}{extension}"

        if lead_id and message_id:
            object_path = (
                f"attachments/{user_id}/"
                f"{lead_id}/{message_id}/{file_name}"
            )

        elif message_id and not lead_id:
            object_path = f"attachments/{user_id}/{message_id}/{file_name}"
        else:
            raise ValueError(
                "Either lead_id or message_id is required"
            )

        blob = self.bucket.blob(object_path)

        await file.seek(0)

        # Blocking GCS operation runs in a separate thread
        upload = partial(
            blob.upload_from_file,
            file.file,
            content_type=file.content_type,
            rewind=True,
        )

        await asyncio.to_thread(upload)

        return {
            "file_name": file.filename,
            "file_path": object_path,
            "file_type": file.content_type,
            "file_size": file.size or 0,
        }

    def generate_signed_url(
        self,
        file_path: str,
        expiration_minutes: int = 300,
    ) -> str:

        print("generating signed url")

        blob = self.bucket.blob(file_path)

        return blob.generate_signed_url(
            version="v4",
            expiration=timedelta(minutes=expiration_minutes),
            method="GET",
        )