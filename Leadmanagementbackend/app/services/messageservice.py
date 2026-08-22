from datetime import datetime

from sqlalchemy.orm import Session

from app.DTOs.MessageDTO import LeadMessagesResponseDTO, MessageDetailsDTO
from app.core.lock import lead_lock_manager
from app.models import Lead
from app.models.messages import Message
from app.repositories.LeadRepository import LeadRepository
from app.repositories.MessageRepository import MessageRepository

from app.enums.message import MessageDirection
from app.enums.message import MessageType


class MessageService:

    def __init__(
            self,
            message_repository: MessageRepository,
            lead_repository: LeadRepository,
    ):
        self.message_repository = (
            message_repository
        )
        self.lead_repository = lead_repository

    async def create_message(
            self,
            lead_id: int | None,
            conversation_id:str | None,
            channel_connection_id: int | None,
            provider_message_id: str | None = None,
            reply_to_message_id: int | None = None,  # Internal Message.id
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

        lock = lead_lock_manager.get_lock(lock_key)

        with lock:
            existing_message = (
                self.message_repository
                .get_by_provider_message_id_and_lead_id(
                    provider_message_id=provider_message_id,
                    lead_id=lead_id,
                    channel_connection_id=channel_connection_id,
                )
            )

            if existing_message:
                return existing_message

            message = Message(
                lead_id=lead_id,
                channel_connection_id=channel_connection_id,
                provider_message_id=provider_message_id,
                conversation_id=conversation_id,

                # Important:
                # This is YOUR DB Message.id, not Gmail's ID
                reply_to_message_id=reply_to_message_id,

                direction=direction,
                sender_identifier=sender_identifier,
                recipient_identifier=recipient_identifier,
                content=content,
                message_type=message_type,
                provider_created_at=provider_created_at,
                
            )

            return self.message_repository.create(message)

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

        lead = (
            self.lead_repository
            .get_by_id(
                lead_id=lead_id
            )
        )

        message_details = []

        for message in messages:
            message_details.append(
                MessageDetailsDTO(
                    id=message.id,

                    direction=message.direction,

                    sender_identifier=(
                        message.sender_identifier
                    ),

                    recipient_identifier=(
                        message.recipient_identifier
                    ),

                    content=message.content,

                    message_type=message.message_type,

                    repliedmessageid=(
                        message.reply_to_message_id
                    ),

                    provider_created_at=(
                        message.provider_created_at
                    ),
                )
            )

        return LeadMessagesResponseDTO(
            lead_id=lead.id,

            lead_name=lead.name,

            lead_email=lead.email,

            lead_phone=lead.phone_number,

            messages=message_details,
        )













