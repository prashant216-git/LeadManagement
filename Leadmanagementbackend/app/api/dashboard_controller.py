from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
)

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.DTOs.DashboardCountDTO import DashboardCountDTO
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


def get_dashboard_service(
    db: AsyncSession = Depends(get_db),
) -> DashboardService:

    dashboard_repository = DashboardRepository(
        db
    )

    return DashboardService(
        dashboard_repository=dashboard_repository
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
    user_id = UUID("9ad69636-f013-49f6-9cce-00f2828dbc6f")

    return await dashboard_service.get_counts(
        user_id=user_id
    )