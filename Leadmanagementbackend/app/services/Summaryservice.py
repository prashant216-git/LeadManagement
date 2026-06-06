from sqlalchemy.orm import Session

from app.models.summary import Summary

from app.services.messageservice import MessageService


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
        summary_text: str,
        last_message_id: int
    ) -> Summary:

        summary = Summary(
            user_id=user_id,
            summary=summary_text,
            last_summarized_message_id=last_message_id
        )

        db.add(summary)
        db.commit()
        db.refresh(summary)

        return summary

    @staticmethod
    def update_summary(
        db: Session,
        user_id: int,
        summary_text: str,
        last_message_id: int
    ) -> Summary:

        summary = SummaryService.get_summary(
            db,
            user_id
        )

        if not summary:

            return SummaryService.create_summary(
                db=db,
                user_id=user_id,
                summary_text=summary_text,
                last_message_id=last_message_id
            )

        summary.summary = summary_text
        summary.last_summarized_message_id = (
            last_message_id
        )

        db.commit()
        db.refresh(summary)

        return summary

    @staticmethod
    def get_summary_text(
        db: Session,
        user_id: int
    ) -> str:

        summary = SummaryService.get_summary(
            db,
            user_id
        )

        if not summary:
            return ""

        return summary.summary or ""

