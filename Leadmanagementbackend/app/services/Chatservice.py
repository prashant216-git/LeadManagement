from datetime import datetime
from uuid import UUID

from app.DTOs.Chats import ChatSidebarDTO, ChatSidebarItemDTO


class ChatService:

    def __init__(
        self,
        lead_repository,
        message_repository,
    ):
        self.lead_repository = lead_repository
        self.message_repository = message_repository

    async def get_chat_sidebar(
        self,
        channel_id: UUID,
            user_id: UUID,
    ) -> ChatSidebarDTO:

        leads, _ = (
            self.lead_repository
            .get_leads_by_channel_id(
                user_id = user_id,
                channel_id=channel_id,
                limit=100,
                offset=0,
                sort_by="updated_at",
                sort_order="desc",
            )
        )
        leads = [
            {
                "lead": lead,
                "status": status_name,
                "status_updated_at": status_updated_at,
            }
            for (
                lead,
                _,
                status_name,
                status_updated_at,
            ) in leads
        ]

        chats = []

        for leads in leads:
            lead=leads["lead"]

            message = (
                self.message_repository
                .get_latest_messages_by_lead_id(
                    lead_id=lead.id,
                    limit=1
                )
            )[0]

            chats.append(
                ChatSidebarItemDTO(
                    lead_id=lead.id,
                    name=lead.name,
                    email=lead.email,
                    phone_number=lead.phone_number,
                    latest_message=(
                        message.content
                        if message
                        else None
                    ),
                    latest_message_time=(
                        message.provider_created_at
                        if message
                        else None
                    ),
                    status=leads["status"],
                )
            )
            chats.sort(
                key=lambda chat: chat.latest_message_time or datetime.min,
                reverse=True
            )

        return ChatSidebarDTO(
            channel_id=channel_id,
            chats=chats,)
