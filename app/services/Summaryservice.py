from sqlalchemy.orm import Session

from app.models.summary import Summary
from app.services.AIService import AIService
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

    @staticmethod
    def ensure_summary(
            db,
            user_id: int
    ):

        summary = SummaryService.get_summary(
            db=db,
            user_id=user_id
        )

        # ----------------------------------
        # First Summary Generation
        # ----------------------------------

        if not summary:

            messages = (
                MessageService.get_all_messages(
                    db=db,
                    user_id=user_id
                )
            )

            if not messages:
                return None

            summary_text = (
                AIService.generate_initial_summary(
                    messages=messages
                )
            )

            return SummaryService.create_summary(
                db=db,
                user_id=user_id,
                summary_text=summary_text,
                last_message_id=messages[-1].id
            )

        # ----------------------------------
        # Existing Summary
        # ----------------------------------

        new_messages = (
            MessageService.get_messages_after_id(
                db=db,
                user_id=user_id,
                message_id=summary.last_summarized_message_id
            )
        )

        # No need to re-summarize yet
        if len(new_messages) < 5:
            return summary

        updated_summary = (
            AIService.update_summary(
                existing_summary=summary.summary,
                messages=new_messages
            )
        )

        return SummaryService.update_summary(
            db=db,
            user_id=user_id,
            summary_text=updated_summary,
            last_message_id=new_messages[-1].id
        )