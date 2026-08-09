from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.enums.channel import ChannelStatus
from app.models.channel_master import ChannelMaster


class ChannelMasterRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    # ==========================================================
    # Get by ID
    # ==========================================================

    def get_by_id(
        self,
        channel_id: int,
    ) -> ChannelMaster | None:

        result =  self.db.execute(
            select(ChannelMaster)
            .where(
                ChannelMaster.id == channel_id
            )
        )

        return result.scalar_one_or_none()

    # ==========================================================
    # Get by Code
    # ==========================================================

    def get_by_code(
        self,
        channel_code: str,
    ) -> ChannelMaster | None:

        result =  self.db.execute(
            select(ChannelMaster)
            .where(
                ChannelMaster.code == channel_code
            )
        )

        return result.scalar_one_or_none()

    # ==========================================================
    # Get All Active Channels
    # ==========================================================

    async def get_all_active(
        self,
    ) -> list[ChannelMaster]:

        result = await self.db.execute(
            select(ChannelMaster)
            .where(
                ChannelMaster.is_active.is_(True)
            )
            .order_by(
                ChannelMaster.id
            )
        )

        return list(result.scalars().all())

    # ==========================================================
    # Save
    # ==========================================================

    async def save(
        self,
        channel: ChannelMaster,
    ) -> ChannelMaster:

        self.db.add(channel)

        await self.db.commit()

        await self.db.refresh(channel)

        return channel

    def get_all(self) -> list[ChannelMaster]:
        result = self.db.execute(
            select(ChannelMaster)
            .order_by(ChannelMaster.id)
        )

        return result.scalars().all()