from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.Attachements import Attachment


class AttachmentRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def save(
        self,
        attachment: Attachment,
    ) -> Attachment:

        self.db.add(attachment)

        await self.db.commit()
        await self.db.refresh(attachment)

        return attachment

    async def get_by_id(
        self,
        attachment_id: UUID,
    ) -> Attachment | None:

        result = await self.db.execute(
            select(Attachment).where(
                Attachment.id == attachment_id
            )
        )

        return result.scalar_one_or_none()

    async def get_all_by_user(
        self,
        user_id: UUID,
    ) -> list[Attachment]:

        result = await self.db.execute(
            select(Attachment)
            .where(
                Attachment.user_id == user_id
            )
            .order_by(
                Attachment.created_at.desc()
            )
        )

        return list(result.scalars().all())

    async def get_by_lead(
        self,
        lead_id: UUID,
    ) -> list[Attachment]:

        result = await self.db.execute(
            select(Attachment)
            .where(
                Attachment.lead_id == lead_id
            )
            .order_by(
                Attachment.created_at.desc()
            )
        )

        return list(result.scalars().all())

    async def get_by_message(
        self,
        message_id: UUID,
    ) -> list[Attachment]:

        result = await self.db.execute(
            select(Attachment)
            .where(
                Attachment.message_id == message_id
            )
            .order_by(
                Attachment.created_at.desc()
            )
        )

        return list(result.scalars().all())