from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.channel_credential import ChannelCredential


class ChannelCredentialRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    def get_by_connection_id(
        self,
        connection_id: UUID,
    ) -> ChannelCredential | None:

        result = self.db.execute(
            select(ChannelCredential).where(
                ChannelCredential.channel_connection_id == connection_id
            )
        )

        return result.scalar_one_or_none()

    def save(
        self,
        credential: ChannelCredential,
    ) -> ChannelCredential:

        self.db.add(credential)
        self.db.flush()

        return credential

    def update(
            self,
            credential,
    ):
        self.db.add(credential)

        self.db.commit()

        self.db.refresh(credential)

        return credential