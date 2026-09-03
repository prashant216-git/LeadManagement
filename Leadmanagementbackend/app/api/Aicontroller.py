from uuid import UUID

from fastapi import APIRouter, Depends
from requests import Session

from app.ai.ai_service import AIService
from app.channel_engine.channelresolver import ChannelResolver
from app.db.session import get_db
from app.dependencies.services import get_message_service, get_channel_resolver, get_summary_service, get_ai_service
from app.services.Summaryservice import SummaryService
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
        channel_resolver : ChannelResolver = Depends(get_channel_resolver),
ai_service: AIService = Depends(get_ai_service),
):


    user_id=UUID("9ad69636-f013-49f6-9cce-00f2828dbc6f")



    if not last_message:
        return None



    return await ai_service.generate_draft(
        user_id=user_id,

        lead_id=lead_id,
        last_message_id=last_message,

    )

@router.post("/{lead_id}/summarise")
async def summarise_lead(
    lead_id: UUID,
    summary_service: SummaryService = Depends(
        get_summary_service
    ),
):
    user_summary, sales_summary = (
        await summary_service.ensure_summary(
            lead_id=lead_id
        )
    )

    return {
        "lead_id": lead_id,
        "user_summary": user_summary,
        "sales_summary": sales_summary,
    }