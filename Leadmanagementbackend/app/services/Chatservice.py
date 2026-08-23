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
        channel_id: int,
    ) -> ChatSidebarDTO:

        leads, _ = (
            self.lead_repository
            .get_leads_by_channel_id(
                tenant_id=1,
                channel_id=channel_id,
                limit=100,
                offset=0,
                sort_by="created_at",
                sort_order="desc",
            )
        )
        leads = [lead for lead, _ in leads]

        chats = []

        for lead in leads:

            message = (
                self.message_repository
                .get_latest_message_by_lead_id(
                    lead_id=lead.id
                )
            )

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
                )
            )

        return ChatSidebarDTO(
            channel_id=channel_id,
            chats=chats,)
