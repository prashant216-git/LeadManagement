from datetime import datetime

from temporalio import workflow

from datetime import timedelta

with workflow.unsafe.imports_passed_through():
    from app.schedulers.temporal.activities.SchedulerMessageActivity import (
        send_scheduled_message,
    )


@workflow.defn
class ScheduledMessageWorkflow:

    @workflow.run
    async def run(
        self,
        scheduled_message_id: str,

    ):



        await workflow.execute_activity(
            send_scheduled_message,
            scheduled_message_id,
            start_to_close_timeout=timedelta(
                minutes=2
            ),
        )