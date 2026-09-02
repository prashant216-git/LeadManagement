from uuid import UUID

from fastapi import APIRouter, Depends
from requests import Session

from app.ai.ai_service import AIService
from app.channel_engine.channelresolver import ChannelResolver
from app.db.session import get_db
from app.dependencies.services import get_message_service, get_channel_resolver
from app.services.messageservice import MessageService

router = APIRouter(
    prefix="/Ai",
    tags=["service"],
)

@router.get("/draft")
async def get_draft(
    lead_id: UUID,
        last_message:UUID,

    db: Session = Depends(get_db),
messageservice: MessageService = Depends(get_message_service),
        channel_resolver : ChannelResolver = Depends(get_channel_resolver)
):
    ai_service = AIService(
        db=db,
        messageservice=messageservice,
        channel_resolver=channel_resolver
    )

    user_id=UUID("9ad69636-f013-49f6-9cce-00f2828dbc6f")



    if not last_message:
        return None



    return await ai_service.generate_draft(
        user_id=user_id,

        lead_id=lead_id,
        last_message_id=last_message,

    )