from app.services.SUmmaryorchestran import DraftGenerationService

from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session  import get_db

from app.DTOs.AIDraftDTO import DraftDTO




router = APIRouter(
    prefix="/drafts",
    tags=["Drafts"]
)


@router.get(
    "/{user_id}",
    response_model=DraftDTO | None
)
def get_draft(
    user_id: int,
    db: Session = Depends(get_db)
):

    return (
        DraftGenerationService
        .get_or_create_draft_for_user(
            db=db,
            user_id=user_id
        )
    )