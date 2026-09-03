from uuid import UUID

from app.ai.ai_service import AIService
from app.models import Summary
from app.repositories.MessageRepository import MessageRepository
from app.repositories.SummaryRepository import SummaryRepository


class SummaryService:

    def __init__(
        self,
        message_repo: MessageRepository,
        summary_repo: SummaryRepository,
        ai_service: AIService,
    ):
        self.message_repo = message_repo
        self.summary_repo = summary_repo
        self.ai_service = ai_service

    async def ensure_summary(
            self,
            lead_id: UUID,
    ) -> tuple[str, str]:

        summary = await self.summary_repo.get_by_lead_id(
            lead_id=lead_id
        )

        # No summary exists yet.
        # Generate the initial summaries from the full conversation.
        if not summary:
            messages = await self.message_repo.get_messages_by_lead_id(
                lead_id=lead_id
            )

            user_summary = await self.ai_service.generate_summary(
                messages=messages,
                summary_type="user",
            )

            sales_summary = await self.ai_service.generate_summary(
                messages=messages,
                summary_type="salesperson",
            )

            last_user_message = next(
                (
                    message
                    for message in reversed(messages)
                    if message.sender_type == "user"
                ),
                None,
            )

            summary = Summary(
                lead_id=lead_id,
                user_summary=user_summary,
                sales_summary=sales_summary,
                last_summarized_user_message_id=(
                    last_user_message.id
                    if last_user_message
                    else None
                ),
            )

            await self.summary_repo.create(summary)

            return user_summary, sales_summary

        # Summary already exists.
        # Check how many new USER messages have arrived.
        last_message_summarized=self.message_repo.get_by_id(summary.last_summarized_user_message_id)
        new_user_messages = (
            await self.message_repo.get_new_user_messages_for_summary(
                lead_id=lead_id,
                last_summarized_user_message_at=last_message_summarized.provider_created_at,
                role="user",
                ),
            )


        # Less than 10 new USER messages.
        # Return the existing summaries without calling AI.
        if len(new_user_messages) < 10:
            return (
                summary.user_summary,
                summary.sales_summary,
            )

        # 10 or more new USER messages.
        # Generate updated summaries using the FULL conversation.
        messages = await self.message_repo.get_new_user_messages_for_summary(
            lead_id=lead_id,
            last_summarized_user_message_at=last_message_summarized.provider_created_at
        )

        user_summary = await self.ai_service.generate_summary(
            messages=messages,
            summary_type="user",
            existing_summary=summary.user_summary,
        )

        sales_summary = await self.ai_service.generate_summary(
            messages=messages,
            summary_type="salesperson",
            existing_summary=summary.sales_summary,
        )

        last_message=new_user_messages[-1]


        summary.user_summary = user_summary
        summary.sales_summary = sales_summary
        summary.last_summarized_user_message_id = last_message.id

        await self.summary_repo.update(summary)

        return user_summary, sales_summary