from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.Users import User


class UserRepository:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    def get_by_gmail(
        self,
        gmail: str,
    ) -> User | None:

        result = self.db.execute(
            select(User).where(
                User.email == gmail
            )
        )

        return result.scalar_one_or_none()