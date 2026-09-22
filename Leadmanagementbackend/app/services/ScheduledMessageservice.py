from datetime import datetime
from uuid import UUID

from app.models.scheduled_message import (
    ScheduledMessage,
    ScheduledMessageStatus,
)
from app.schedulers.temporal.workflows.SchedulerMessageWorkflow import ScheduledMessageWorkflow


class ScheduledMessageService:

    def __init__(
        self,
        scheduled_message_repository,
            temporal_dyanmic_registrar,
    ):
        self.scheduled_message_repository = (
            scheduled_message_repository
        )
        self.temporal_dyanmic_registrar=temporal_dyanmic_registrar

    async def schedule_message(
        self,
        user_id: UUID,
        lead_id: UUID,
        channel_connection_id: UUID,
        content: str,
        scheduled_at: datetime,
    ) -> ScheduledMessage:

        scheduled_message = ScheduledMessage(
            user_id=user_id,
            lead_id=lead_id,
            channel_connection_id=channel_connection_id,
            content=content,
            scheduled_at=scheduled_at,
            status=ScheduledMessageStatus.SCHEDULED,
        )
        scheduled_message=self.scheduled_message_repository.create(
            scheduled_message
        )
        print("creating worfkloew")
        await self.temporal_dyanmic_registrar.register(
            schedule_id=f"scheduled-message-{scheduled_message.id}",
            workflow=ScheduledMessageWorkflow.run,
            args=[
                str(scheduled_message.id),
            ],
            start_at=scheduled_message.scheduled_at,
        )

        return scheduled_message