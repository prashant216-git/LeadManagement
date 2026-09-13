from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.scheduler_history import SchedulerHistory


class SchedulerHistoryRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(
        self,
        history_id: UUID,
    ) -> SchedulerHistory | None:

        statement = select(SchedulerHistory).where(
            SchedulerHistory.id == history_id
        )

        return self.db.execute(
            statement
        ).scalar_one_or_none()

    def get_by_workflow_id(
        self,
        workflow_id: str,
    ) -> SchedulerHistory | None:

        statement = select(SchedulerHistory).where(
            SchedulerHistory.temporal_workflow_id
            == workflow_id
        )

        return self.db.execute(
            statement
        ).scalar_one_or_none()

    def get_by_entity(
        self,
        scheduler_master_id: UUID,
        entity_type: str,
        entity_id: UUID,
    ) -> SchedulerHistory | None:

        statement = select(SchedulerHistory).where(
            SchedulerHistory.scheduler_master_id
            == scheduler_master_id,
            SchedulerHistory.entity_type == entity_type,
            SchedulerHistory.entity_id == entity_id,
        )

        return self.db.execute(
            statement
        ).scalar_one_or_none()

    def create(
        self,
        history: SchedulerHistory,
    ) -> SchedulerHistory:

        self.db.add(history)
        self.db.commit()
        self.db.refresh(history)

        return history

    def mark_running(
        self,
        history_id: UUID,
        temporal_run_id: str,
    ) -> SchedulerHistory | None:

        history = self.get_by_id(history_id)

        if history is None:
            return None

        history.status = "RUNNING"
        history.temporal_run_id = temporal_run_id
        history.started_at = datetime.utcnow()
        history.attempt_count += 1

        self.db.commit()
        self.db.refresh(history)

        return history

    def mark_completed(
        self,
        history_id: UUID,
    ) -> SchedulerHistory | None:

        history = self.get_by_id(history_id)

        if history is None:
            return None

        history.status = "COMPLETED"
        history.completed_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(history)

        return history

    def mark_failed(
        self,
        history_id: UUID,
        error_message: str,
    ) -> SchedulerHistory | None:

        history = self.get_by_id(history_id)

        if history is None:
            return None

        history.status = "FAILED"
        history.error_message = error_message

        self.db.commit()
        self.db.refresh(history)

        return history

    def update_status(
        self,
        history_id: UUID,
        status: str,
        error_message: str | None = None,
    ) -> SchedulerHistory | None:

        history = self.get_by_id(history_id)

        if history is None:
            return None

        history.status = status
        history.error_message = error_message

        self.db.commit()
        self.db.refresh(history)

        return history