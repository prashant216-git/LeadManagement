from fastapi import APIRouter

from app.db.database import SessionLocal
from app.services.AIServiceimpl import AIService
from app.db.session import get_db
router = APIRouter()


@router.get("/aitest")
async def aitest():
    db = SessionLocal()
    AIService.generate_reply(db,user_id=1,message_id=1)