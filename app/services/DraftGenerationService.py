from sqlalchemy.orm import Session

from app.services.SUmmaryorchestran import Summaryimpl
from app.services.AIDraftService import AIDraftService
from app.services.AIServiceimpl import AIService
from app.services.messageservice import MessageService


class DraftGenerationService:
    @staticmethod

    def get_or_create_draft_for_user(
            db: Session,
            user_id: int
    ):

        latest_message = (
            MessageService.get_latest_message(
                db=db,
                user_id=user_id
            )
        )

        if not latest_message:
            return None

        if latest_message.sender != "user":
            return None

        existing_draft = (
            AIDraftService.get_by_message_id(
                db=db,
                message_id=latest_message.id
            )
        )

        if existing_draft:
            return AIDraftService.to_dto(existing_draft)

        Summaryimpl.ensure_summary(
            db=db,
            user_id=user_id
        )
        print("calling llm generating reply")

        draft_text = (
            AIService.generate_reply(
                db=db,
                user_id=user_id
            )
        )

        draft = (
            AIDraftService.create_draft(
                db=db,
                user_id=user_id,
                message_id=latest_message.id,
                draft_text=draft_text
            )
        )
        return AIDraftService.to_dto(draft)