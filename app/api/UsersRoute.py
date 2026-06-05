from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.DTOs.UserChatDTO import UserChatDTO
from app.db.session import get_db
from app.services.ChatService import ChatService
from app.DTOs.Chats import ChatSidebarDTO

router = APIRouter(
    prefix="/chats",
    tags=["Chats"]
)


@router.get(
    "",
    response_model=list[ChatSidebarDTO]
)
def get_chats(
    db: Session = Depends(get_db)
):
    return ChatService.get_chat_sidebar(db)

@router.get(
    "/{user_id}",
    response_model=UserChatDTO
)
def get_user_chat(
    user_id: int,
    db: Session = Depends(get_db)
):
    return ChatService.get_user_chat(
        db,
        user_id
    )