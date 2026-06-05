from sqlalchemy.orm import Session

from app.models.summary import Summary


class SummaryService:

    @staticmethod
    def get_summary(
        db: Session,
        user_id: int
    ) -> Summary | None:

        return (
            db.query(Summary)
            .filter(
                Summary.user_id == user_id
            )
            .first()
        )

    @staticmethod
    def create_summary(
        db: Session,
        user_id: int,
        summary_text: str = ""
    ) -> Summary:

        summary = Summary(
            user_id=user_id,
            summary=summary_text
        )

        db.add(summary)
        db.commit()
        db.refresh(summary)

        return summary

    @staticmethod
    def get_or_create_summary(
        db: Session,
        user_id: int
    ) -> Summary:

        summary = SummaryService.get_summary(
            db=db,
            user_id=user_id
        )

        if summary:
            return summary

        return SummaryService.create_summary(
            db=db,
            user_id=user_id
        )

    @staticmethod
    def update_summary(
        db: Session,
        user_id: int,
        summary_text: str
    ) -> Summary:

        summary = SummaryService.get_or_create_summary(
            db=db,
            user_id=user_id
        )

        summary.summary = summary_text

        db.commit()
        db.refresh(summary)

        return summary

    @staticmethod
    def get_summary_text(
        db: Session,
        user_id: int
    ) -> str:

        summary = SummaryService.get_summary(
            db=db,
            user_id=user_id
        )

        if not summary:
            return ""

        return summary.summary or ""