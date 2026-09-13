from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.scheduler_master import SchedulerMaster


class SchedulerMasterRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(
        self,
        scheduler_id: UUID,
    ) -> SchedulerMaster | None:

        statement = select(SchedulerMaster).where(
            SchedulerMaster.id == scheduler_id
        )

        return self.db.execute(
            statement
        ).scalar_one_or_none()

    def get_by_code(
        self,
        scheduler_code: str,
    ) -> SchedulerMaster | None:

        statement = select(SchedulerMaster).where(
            SchedulerMaster.scheduler_code == scheduler_code
        )

        return self.db.execute(
            statement
        ).scalar_one_or_none()

    def get_enabled_schedulers(
        self,
    ) -> list[SchedulerMaster]:

        statement = select(SchedulerMaster).where(
            SchedulerMaster.enabled.is_(True)
        )

        return list(
            self.db.execute(statement).scalars().all()
        )

    def get_enabled_static_schedulers(
        self,
    ) -> list[SchedulerMaster]:

        statement = select(SchedulerMaster).where(
            SchedulerMaster.scheduler_type
            == "STATIC_RECURRING",
            SchedulerMaster.enabled.is_(True),
        )

        return list(
            self.db.execute(statement).scalars().all()
        )

    def create(
        self,
        scheduler: SchedulerMaster,
    ) -> SchedulerMaster:

        self.db.add(scheduler)
        self.db.commit()
        self.db.refresh(scheduler)

        return scheduler

    def update_enabled(
        self,
        scheduler_id: UUID,
        enabled: bool,
    ) -> SchedulerMaster | None:

        scheduler = self.get_by_id(scheduler_id)

        if scheduler is None:
            return None

        scheduler.enabled = enabled

        self.db.commit()
        self.db.refresh(scheduler)

        return scheduler