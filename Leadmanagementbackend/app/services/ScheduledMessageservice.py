from datetime import datetime
from uuid import UUID

from app.DTOs.MessageDTO import ScheduledMessageResponse

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

    async def get_by_lead_id(self, lead_id: UUID) -> list[ScheduledMessageResponse] | None:

        schedule_messages=self.scheduled_message_repository.get_by_lead_id_scheduled(lead_id=lead_id)

        valid_messages=[]

        for scheduled_message in schedule_messages:
            valid_messages.append(ScheduledMessageResponse(
                id=scheduled_message.id,
                lead_id=scheduled_message.lead_id,
                content=scheduled_message.content,
                channel_connection_id=scheduled_message.channel_connection_id,
                scheduled_at=scheduled_message.scheduled_at,
                status=scheduled_message.status,

            ))
        return valid_messages

    async def cancel_message(
            self,
            scheduled_message_id: UUID,
    ) -> ScheduledMessage:

        scheduled_message = (
            await self.scheduled_message_repository.get_by_id(
                scheduled_message_id
            )
        )

        if not scheduled_message:
            raise ValueError("Scheduled message not found")

        if scheduled_message.status != ScheduledMessageStatus.SCHEDULED:
            raise ValueError("Scheduled message cannot be cancelled")

        schedule_id = f"scheduled-message-{scheduled_message.id}"

        # Cancel Temporal schedule first
        await self.temporal_dyanmic_registrar.cancel(
            schedule_id=schedule_id
        )

        # Update DB
        scheduled_message.status = ScheduledMessageStatus.CANCELLED

        await self.scheduled_message_repository.update(
            scheduled_message
        )

        return scheduled_message



