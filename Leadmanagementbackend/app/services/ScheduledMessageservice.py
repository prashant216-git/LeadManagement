from datetime import datetime
from uuid import UUID

from app.models.scheduled_message import (
    ScheduledMessage,
    ScheduledMessageStatus,
)


class ScheduledMessageService:

    def __init__(
        self,
        scheduled_message_repository,
            temporal_dyanmic_repository,
    ):
        self.scheduled_message_repository = (
            scheduled_message_repository
        )
        self.temporal_dyanmic_repository=temporal_dyanmic_repository

    def schedule_message(
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

        return self.scheduled_message_repository.create(
            scheduled_message
        )