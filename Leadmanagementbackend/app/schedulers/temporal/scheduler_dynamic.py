
from temporalio.client import (
    Schedule,
    ScheduleActionStartWorkflow,
    ScheduleCalendarSpec,
    ScheduleRange,
    ScheduleSpec,
)

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
        print("SCHEDULE ID:", schedule_id)
        print("WORKFLOW:", workflow)
        print("ARGS:", args)
        print("START_AT:", start_at)
        print("START_AT TYPE:", type(start_at))

        calendar = ScheduleCalendarSpec(
            year=[ScheduleRange(start_at.year)],
            month=[ScheduleRange(start_at.month)],
            day_of_month=[ScheduleRange(start_at.day)],
            hour=[ScheduleRange(start_at.hour)],
            minute=[ScheduleRange(start_at.minute)],
            second=[ScheduleRange(start_at.second)],
        )

        spec = ScheduleSpec(
            calendars=[calendar],
            time_zone_name="UTC",
        )

        schedule = Schedule(
            action=ScheduleActionStartWorkflow(
                workflow,
                args=args,
                id=f"{schedule_id}-workflow",
                task_queue=settings.TEMPORAL_TASK_QUEUE,
            ),
            spec=spec,
        )

        print("WORKFLOW ID:", f"{schedule_id}-workflow")
        print("SCHEDULE SPEC:", schedule.spec)
        print("CALENDAR:", schedule.spec.calendars)
        print("TIMEZONE:", schedule.spec.time_zone_name)

        await self.client.create_schedule(
            schedule_id,
            schedule,
        )

        handle = self.client.get_schedule_handle(schedule_id)

        description = await handle.describe()

        print("=== TEMPORAL SCHEDULE ===")
        print("INFO:", description.info)
        print("SPEC:", description.schedule.spec)
        print("NEXT ACTION TIMES:", description.info.next_action_times)
        print("=========================")

