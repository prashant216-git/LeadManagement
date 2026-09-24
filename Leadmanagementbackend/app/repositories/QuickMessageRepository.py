from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.Quick_message_attachement_config import Quick_message_attachement_config


class QuickMessageRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def save(
        self,
        quick_message: Quick_message_attachement_config,
    ) -> Quick_message_attachement_config:

        self.db.add(quick_message)

        self.db.add(quick_message)
        await self.db.flush()
        await self.db.refresh(quick_message)

        return quick_message

    async def get_by_id(
        self,
        quick_message_id: UUID,
    ) -> Quick_message_attachement_config | None:

        result = await self.db.execute(
            select(Quick_message_attachement_config).where(
                Quick_message_attachement_config.id == quick_message_id
            )
        )

        return result.scalar_one_or_none()

    async def get_all_by_user(
        self,
        user_id: UUID,
    ) -> list[Quick_message_attachement_config]:

        result = await self.db.execute(
            select(Quick_message_attachement_config)
            .where(
                Quick_message_attachement_config.user_id == user_id
            )
            .order_by(
                Quick_message_attachement_config.created_at.desc()
            )
        )

        return list(result.scalars().all())