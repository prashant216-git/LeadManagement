from uuid import UUID

from fastapi.params import Depends
from sqlalchemy.ext.asyncio import result

from app.DTOs.AIDraftDTO import DraftDTO
from app.ai.prompts.summary_prompt import SALES_SUMMARY_PROMPT, SALES_SUMMARY_UPDATE_PROMPT, USER_SUMMARY_PROMPT, \
    USER_SUMMARY_UPDATE_PROMPT
from app.ai.providers.deepseek_provider import DeepSeekProvider
from app.ai.prompts.draft_prompt import DRAFT_REPLY_PROMPT
from app.channel_engine.channelresolver import ChannelResolver

from app.enums.message import MessageDirection, AIDraftStatus
from app.models import Message
from app.repositories.AI_DraftRepository import AIDraftRepository
from app.services.messageservice import MessageService
from app.models.Ai_Draft import AIDraft


class AIService:

    def __init__(
            self,
            db,
            messageservice,
            channel_resolver : ChannelResolver,


    ):
        self.db = db
        self.provider = DeepSeekProvider()
        self.messageservice = messageservice
        self.ai_draft_repository=AIDraftRepository(db)
        self.channel_resolver=channel_resolver

    async def generate_draft(
            self,
            user_id: UUID,
            lead_id: UUID,
            last_message_id: UUID,
    ) -> DraftDTO:

        print(last_message_id)
        print(lead_id)
        # ---------------------------------------------
        # 1. Fetch relevant data
        # ---------------------------------------------

        # Lead information
        # Conversation history
        # Existing summary
        # etc.

        # ---------------------------------------------
        # 2. Build context
        # ---------------------------------------------
        existing_draft = self.ai_draft_repository.get_by_message_id(last_message_id)
        if existing_draft:
            return DraftDTO(status=existing_draft.status,
                        draft_text=existing_draft.draft_text,
                        message_id=existing_draft.message_id,
                        draft_id=existing_draft.id)

        last_messages = await self.messageservice.get_latest_messages_by_lead(lead_id= lead_id,limit=6)
        print(last_messages)
        last_message= self.channel_resolver.resolve_message_id(last_message_id)
        print(last_message)

        context = self._build_conversation_context(last_messages)
        context = "\n".join([
            context,
            "Last message from customer is:",
            last_message.content,
        ])



        # ---------------------------------------------
        # 3. Build prompt
        # ---------------------------------------------

        prompt = DRAFT_REPLY_PROMPT.format(
            context=context
        )

        result=self.provider.generate(prompt)

        draft = AIDraft(
            lead_id=lead_id,
            user_id=user_id,
            message_id=last_message_id,
            draft_text=result,
            status=AIDraftStatus.GENERATED,
        )
        self.ai_draft_repository.create(draft)
        self.db.commit()


        # ---------------------------------------------
        # 4. Generate response
        # ---------------------------------------------

        return DraftDTO(status=AIDraftStatus.GENERATED,
                        draft_text=result,
                        message_id=last_message_id,
                        draft_id=draft.id)

    async def generate_summary(
            self,
            messages: list[Message],
            summary_type: str,
            existing_summary: str | None = None,
    ) -> str:

        context = self._build_conversation_context(messages)

        if summary_type == "user":
            if existing_summary:
                prompt = USER_SUMMARY_UPDATE_PROMPT.format(
                    existing_summary=existing_summary,
                    context=context,
                )
            else:
                prompt = USER_SUMMARY_PROMPT.format(
                    context=context,
                )

        elif summary_type == "salesperson":
            if existing_summary:
                prompt = SALES_SUMMARY_UPDATE_PROMPT.format(
                    existing_summary=existing_summary,
                    context=context,
                )
            else:
                prompt = SALES_SUMMARY_PROMPT.format(
                    context=context,
                )

        else:
            raise ValueError(f"Invalid summary type: {summary_type}")

        result=self.provider.generate(prompt)

        return result

    def _build_conversation_context(
            self,
            messages: list[Message],
    ) -> str:

        conversation = []

        for message in messages:

            if message.direction == MessageDirection.INBOUND:
                sender = "CUSTOMER"
            elif message.direction == MessageDirection.OUTBOUND:
                sender = "SALES"
            else:
                sender = "UNKNOWN"

            conversation.append(
                f"{sender}: {message.content}"
            )

        return "\n".join(conversation)