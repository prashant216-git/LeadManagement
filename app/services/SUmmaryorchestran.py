import this

from sqlalchemy.orm import Session

from app.services.messageservice import MessageService
from app.services.Summaryservice import SummaryService
from app.services.AIDraftService import AIDraftService
from app.services.AIServiceimpl import AIService


class Summaryimpl:



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