# app/schedulers/temporal/workflows/gmail_watch_renewal_workflow.py

from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from app.schedulers.temporal.activities.gmail_watch_renewal_activity import (
        renew_expiring_channel_watches,
    )


@workflow.defn
class GmailWatchRenewalWorkflow:

    @workflow.run
    async def run(self) -> None:
        await workflow.execute_activity(
            renew_expiring_channel_watches,
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=RetryPolicy(
                maximum_attempts=3,
            ),
        )