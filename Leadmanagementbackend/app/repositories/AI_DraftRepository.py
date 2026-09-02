from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.Ai_Draft import AIDraft
from app.enums.message import AIDraftStatus


class AIDraftRepository:

    def __init__(self, db: Session):
        self.db = db

    # ---------------------------------------------------------
    # Create
    # ---------------------------------------------------------

    def create(self, draft: AIDraft) -> AIDraft:
        self.db.add(draft)
        self.db.flush()

        return draft

    # ---------------------------------------------------------
    # Get by ID
    # ---------------------------------------------------------

    def get_by_id(
        self,
        draft_id: UUID,
    ) -> AIDraft | None:

        statement = (
            select(AIDraft)
            .where(AIDraft.id == draft_id)
        )

        result = self.db.execute(statement)

        return result.scalar_one_or_none()

    # ---------------------------------------------------------
    # Get draft by message
    # ---------------------------------------------------------

    def get_by_message_id(
        self,
        message_id: UUID,
    ) -> AIDraft | None:

        statement = (
            select(AIDraft)
            .where(AIDraft.message_id == message_id)
        )

        result = self.db.execute(statement)

        return result.scalar_one_or_none()

    # ---------------------------------------------------------
    # Get latest draft for user
    # ---------------------------------------------------------

    def get_latest_by_user_id(
        self,
        user_id: UUID,
    ) -> AIDraft | None:

        statement = (
            select(AIDraft)
            .where(AIDraft.user_id == user_id)
            .order_by(AIDraft.created_at.desc())
            .limit(1)
        )

        result = self.db.execute(statement)

        return result.scalar_one_or_none()

    # ---------------------------------------------------------
    # Update draft text
    # ---------------------------------------------------------

    def update_text(
        self,
        draft_id: UUID,
        draft_text: str,
    ) -> AIDraft | None:

        draft = self.get_by_id(draft_id)

        if draft is None:
            return None

        draft.draft_text = draft_text
        draft.status = AIDraftStatus.EDITED

        self.db.commit()
        self.db.refresh(draft)

        return draft

    # ---------------------------------------------------------
    # Update status
    # ---------------------------------------------------------

    def update_status(
        self,
        draft_id: UUID,
        status: AIDraftStatus,
    ) -> AIDraft | None:

        draft = self.get_by_id(draft_id)

        if draft is None:
            return None

        draft.status = status

        self.db.commit()
        self.db.refresh(draft)

        return draft

    # ---------------------------------------------------------
    # Mark as sent
    # ---------------------------------------------------------

    def mark_sent(
        self,
        draft_id: UUID,
    ) -> AIDraft | None:

        return self.update_status(
            draft_id=draft_id,
            status=AIDraftStatus.SENT,
        )

    # ---------------------------------------------------------
    # Discard
    # ---------------------------------------------------------

    def discard(
        self,
        draft_id: UUID,
    ) -> AIDraft | None:

        return self.update_status(
            draft_id=draft_id,
            status=AIDraftStatus.DISCARDED,
        )