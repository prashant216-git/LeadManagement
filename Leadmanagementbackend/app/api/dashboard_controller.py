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
    tenant_id=1

    return await dashboard_service.get_counts(
        tenant_id=tenant_id
    )