from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
)

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.DTOs.DashboardCountDTO import DashboardCountDTO
from app.dependencies.services import get_dashboard_service
from app.repositories.DashboardRepository import (
    DashboardRepository,
)
from app.services.DashboardService import (
    DashboardService,
)


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)





@router.get(
    "/counts",
    response_model=DashboardCountDTO,
)
async def get_dashboard_counts(

    dashboard_service: DashboardService = Depends(
        get_dashboard_service
    ),
):
    user_id = UUID("09a81c46-92c4-42ae-9ffe-4275d62f1d9f")

    return await dashboard_service.get_counts(
        user_id=user_id
    )