from sqlalchemy.orm import Session

from app.models.Ai_Draft import AIDraft


class AIDraftService:

    @staticmethod
    def create_draft(
        db: Session,
        user_id: int,
        message_id: int,
        draft_text: str
    ) -> AIDraft:

        draft = AIDraft(
            user_id=user_id,
            message_id=message_id,
            draft_text=draft_text,
            status="generated"
        )

        db.add(draft)
        db.commit()
        db.refresh(draft)

        return draft

    @staticmethod
    def get_draft(
        db: Session,
        draft_id: int
    ) -> AIDraft | None:

        return (
            db.query(AIDraft)
            .filter(
                AIDraft.id == draft_id
            )
            .first()
        )

    @staticmethod
    def get_latest_draft(
        db: Session,
        user_id: int
    ) -> AIDraft | None:

        return (
            db.query(AIDraft)
            .filter(
                AIDraft.user_id == user_id
            )
            .order_by(
                AIDraft.created_at.desc()
            )
            .first()
        )

    @staticmethod
    def get_drafts_for_message(
        db: Session,
        message_id: int
    ) -> list[AIDraft]:

        return (
            db.query(AIDraft)
            .filter(
                AIDraft.message_id == message_id
            )
            .order_by(
                AIDraft.created_at.desc()
            )
            .all()
        )

    @staticmethod
    def approve_draft(
        db: Session,
        draft_id: int
    ) -> AIDraft | None:

        draft = AIDraftService.get_draft(
            db=db,
            draft_id=draft_id
        )

        if not draft:
            return None

        draft.status = "approved"

        db.commit()
        db.refresh(draft)

        return draft

    @staticmethod
    def reject_draft(
        db: Session,
        draft_id: int
    ) -> AIDraft | None:

        draft = AIDraftService.get_draft(
            db=db,
            draft_id=draft_id
        )

        if not draft:
            return None

        draft.status = "rejected"

        db.commit()
        db.refresh(draft)

        return draft

    @staticmethod
    def mark_sent(
        db: Session,
        draft_id: int
    ) -> AIDraft | None:

        draft = AIDraftService.get_draft(
            db=db,
            draft_id=draft_id
        )

        if not draft:
            return None

        draft.status = "sent"

        db.commit()
        db.refresh(draft)

        return draft

    @staticmethod
    def update_draft_text(
        db: Session,
        draft_id: int,
        draft_text: str
    ) -> AIDraft | None:

        draft = AIDraftService.get_draft(
            db=db,
            draft_id=draft_id
        )

        if not draft:
            return None

        draft.draft_text = draft_text
        draft.status = "edited"

        db.commit()
        db.refresh(draft)

        return draft