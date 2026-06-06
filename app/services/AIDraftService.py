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
            .filter(AIDraft.id == draft_id)
            .first()
        )

    @staticmethod
    def get_by_message_id(
        db: Session,
        message_id: int
    ) -> AIDraft | None:

        return (
            db.query(AIDraft)
            .filter(
                AIDraft.message_id == message_id
            )
            .order_by(
                AIDraft.created_at.desc()
            )
            .first()
        )

    @staticmethod
    def get_latest_draft_for_user(
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
    def update_draft_text(
        db: Session,
        draft_id: int,
        draft_text: str
    ) -> AIDraft | None:

        draft = AIDraftService.get_draft(
            db,
            draft_id
        )

        if not draft:
            return None

        draft.draft_text = draft_text
        draft.status = "edited"

        db.commit()
        db.refresh(draft)

        return draft

    @staticmethod
    def mark_sent(
        db: Session,
        draft_id: int
    ) -> AIDraft | None:

        draft = AIDraftService.get_draft(
            db,
            draft_id
        )

        if not draft:
            return None

        draft.status = "sent"

        db.commit()
        db.refresh(draft)

        return draft

    @staticmethod
    def delete_draft(
        db: Session,
        draft_id: int
    ) -> bool:

        draft = AIDraftService.get_draft(
            db,
            draft_id
        )

        if not draft:
            return False

        db.delete(draft)
        db.commit()

        return True

    @staticmethod
    def get_or_create_draft_for_message(
        db: Session,
        user_id: int,
        message_id: int,
        generator_func
    ) -> AIDraft:

        existing_draft = (
            AIDraftService.get_by_message_id(
                db,
                message_id
            )
        )

        if existing_draft:
            return existing_draft

        draft_text = generator_func()

        return (
            AIDraftService.create_draft(
                db=db,
                user_id=user_id,
                message_id=message_id,
                draft_text=draft_text
            )
        )

    @staticmethod
    def to_dto(
            draft: AIDraft
    ) -> DraftDTO:

        return DraftDTO(
            draft_id=draft.id,
            user_id=draft.user_id,
            message_id=draft.message_id,
            draft_text=draft.draft_text,
            status=draft.status
        )



