from temporalio.client import Schedule, ScheduleActionStartWorkflow, ScheduleSpec

from app.core.config import settings


class TemporalScheduler:

    def __init__(self, client):
        self.client = client

    async def register(
        self,
        schedule_id: str,
        workflow,
        args: list,
        start_at,
    ):
        schedule = Schedule(
            action=ScheduleActionStartWorkflow(
                workflow,
                args=args,
                id=f"{schedule_id}-workflow",
                task_queue=settings.TEMPORAL_TASK_QUEUE,
            ),
            spec=ScheduleSpec(
                start_at=start_at,
            ),
        )

        await self.client.create_schedule(
            schedule_id,
            schedule,
        )