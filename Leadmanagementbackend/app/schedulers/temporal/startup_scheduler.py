from temporalio.client import (
    Client,
    Schedule,
    ScheduleActionStartWorkflow,
    ScheduleCalendarSpec,
    ScheduleRange,
    ScheduleSpec,
    ScheduleUpdate,
)

from app.core.config import settings

from app.schedulers.temporal.workflows.gmail_watch_renewal_workflow import (
    GmailWatchRenewalWorkflow,
)


STATIC_SCHEDULERS = [
    {
        "id": "gmail-watch-renewal",
        "workflow": GmailWatchRenewalWorkflow.run,
        "args": [],
        "hour": 12,
        "minute": 40,
    },
]


async def register_static_schedulers(
    client: Client,
) -> None:

    for scheduler in STATIC_SCHEDULERS:
        schedule_id = scheduler["id"]

        schedule = Schedule(
            action=ScheduleActionStartWorkflow(
                scheduler["workflow"],
                args=scheduler["args"],
                id=f"{schedule_id}-workflow",
                task_queue=settings.TEMPORAL_TASK_QUEUE,
            ),
            spec=ScheduleSpec(
                calendars=[
                    ScheduleCalendarSpec(
                        hour=[
                            ScheduleRange(
                                start=scheduler["hour"],
                                end=scheduler["hour"],
                            )
                        ],
                        minute=[
                            ScheduleRange(
                                start=scheduler["minute"],
                                end=scheduler["minute"],
                            )
                        ],
                    )
                ],

            ),
        )

        try:
            handle = client.get_schedule_handle(schedule_id)

            def update_schedule(current):
                return ScheduleUpdate(
                    schedule=schedule,
                )

            await handle.update(update_schedule)

            print(
                f"Updated Temporal scheduler: {schedule_id}"
            )

        except Exception as exc:
            if "not found" in str(exc).lower():
                await client.create_schedule(
                    schedule_id,
                    schedule,
                )

                print(
                    f"Created Temporal scheduler: {schedule_id}"
                )
            else:
                raise