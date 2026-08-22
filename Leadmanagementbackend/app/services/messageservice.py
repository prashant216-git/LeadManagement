from datetime import datetime

from sqlalchemy.orm import Session

from app.DTOs.MessageDTO import LeadMessagesResponseDTO, MessageDetailsDTO
from app.core.lock import lead_lock_manager
from app.models.messages import Message
from app.repositories.MessageRepository import MessageRepository

from app.enums.message import MessageDirection
from app.enums.message import MessageType


class MessageService:

    def __init__(
            self,
            message_repository: MessageRepository,
    ):
        self.message_repository = (
            message_repository
        )

    async def create_message(
            self,
            lead_id: int | None,
            channel_connection_id: int | None,
            provider_message_id: str | None = None,
            direction: MessageDirection | None = None,
            sender_identifier: str | None = None,
            recipient_identifier: str | None = None,
            content: str | None = None,
            message_type: MessageType | None = None,
            provider_created_at: datetime | None = None,
            provider_metadata: dict | None = None,
    ) -> Message:
        lock_key = (

            f"{lead_id}:"
            f"{provider_message_id}"
        )

        lock = lead_lock_manager.get_lock(
            lock_key
        )


        with lock:
            existmessage = self.message_repository.get_by_provider_message_id_and_lead_id(
                provider_message_id=provider_message_id, lead_id=lead_id,channel_connection_id=channel_connection_id)
            if existmessage:
                return existmessage

            message = Message(
                lead_id=lead_id,
                channel_connection_id=channel_connection_id,
                provider_message_id=provider_message_id,
                direction=direction,
                sender_identifier=sender_identifier,
                recipient_identifier=recipient_identifier,
                content=content,
                message_type=message_type,
                provider_created_at=provider_created_at,
                provider_metadata=provider_metadata,
            )

            return self.message_repository.create(
                message
            )

    async def get_messages_by_lead_id(
                self,
                lead_id: int,
        ) -> LeadMessagesResponseDTO:

            messages = (
                self.message_repository
                .get_messages_by_lead_id(
                    lead_id=lead_id
                )
            )

            message_details = []

            for message in messages:
                message_details.append(
                    MessageDetailsDTO(
                        id=message.id,
                        direction=message.direction,
                        sender_identifier=message.sender_identifier,
                        recipient_identifier=message.recipient_identifier,
                        content=message.content,
                        message_type=message.message_type,
                        provider_created_at=message.provider_created_at,
                    )
                )

            return LeadMessagesResponseDTO(
                lead_id=lead_id,
                messages=message_details,
            )













